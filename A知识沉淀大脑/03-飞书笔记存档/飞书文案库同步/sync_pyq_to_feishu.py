#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朋友圈文案库 → 飞书知识库 自动同步工具
========================================

把本地的 朋友圈文案库（PYQ-*.md）自动同步成飞书知识库里的在线文档。
手机上用飞书 App / 微信里点链接即可随时查看、复制。

原理
----
不依赖飞书「导入」接口（那只能挂云空间），而是直接在知识库里创建 docx 节点，
再把 markdown 转成飞书 block 写入。支持增量覆盖：内容更新后重跑一次即可。

用法
----
    python3 sync_pyq_to_feishu.py --list-spaces     # 查看可见知识库，验证凭据
    python3 sync_pyq_to_feishu.py --dry-run         # 预览会同步哪些文件（不真正写入）
    python3 sync_pyq_to_feishu.py                   # 执行同步

一次性配置步骤见同目录「接入指引.md」。
"""

import argparse
import json
import os
import re
import sys
import time

import requests

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
BASE = "https://open.feishu.cn/open-apis"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 脚本放在 <vault>/99-独立内容/飞书文案库同步/ 下，向上两级即 vault 根目录
VAULT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
# 已有飞书应用（录音同步）的配置，脚本自动复用
FEISHU_CFG = os.path.expanduser("~/.config/feishu-obsidian/config.json")

# 块类型（飞书 docx）
BT_TEXT = 2
BT_HEADING = [3, 4, 5, 6, 7, 8]   # heading1 ~ heading6
BT_BULLET = 12
BT_ORDERED = 13
BT_CODE = 14
BT_QUOTE = 15
BT_DIVIDER = 22

CHUNK = 40          # 每次请求最多写入的块数（接口上限 50）
WRITE_INTERVAL = 0.4  # 接口频率限制 3 次/秒，稍作等待


class FeishuError(Exception):
    """飞书接口返回的异常"""


# ---------------------------------------------------------------------------
# markdown → 飞书 block 转换
# ---------------------------------------------------------------------------
INLINE_RE = re.compile(r"(\*\*[^*]+\*\*|\*[^*\n]+\*|\[[^\]\n]*\]\([^)\n]*\)|`[^`\n]+`)")


def strip_frontmatter(text):
    """去掉 YAML frontmatter"""
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.S)
        if m:
            return text[m.end():]
    return text


def strip_wikilinks(text):
    """[[笔记名]] / [[笔记名|别名]] → 文本"""
    return re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", text)


def run_elem(content, bold=False, italic=False, link=None):
    style = {}
    if bold:
        style["bold"] = True
    if italic:
        style["italic"] = True
    if link:
        style["link"] = {"url": link}
    return {"text_run": {"content": content, "text_element_style": style}}


def inline_elements(text):
    """解析一段文本里的 **加粗**、*斜体*、[链接](url)、`行内代码`"""
    text = strip_wikilinks(text)
    elems = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            elems.append(run_elem(text[pos:m.start()]))
        tok = m.group(0)
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            elems.append(run_elem(tok[2:-2], bold=True))
        elif tok.startswith("[") and "](" in tok and tok.endswith(")"):
            inner = tok[1:-1]
            label, _, url = inner.partition("](")
            elems.append(run_elem(label, link=url))
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            elems.append(run_elem(tok[1:-1]))
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            elems.append(run_elem(tok[1:-1], italic=True))
        else:
            elems.append(run_elem(tok))
        pos = m.end()
    if pos < len(text):
        elems.append(run_elem(text[pos:]))
    if not elems:
        elems.append(run_elem(""))
    return elems


def text_block(elements):
    return {"block_type": BT_TEXT, "text": {"elements": elements, "style": {}}}


def md_to_blocks(text):
    """把 markdown 正文转成飞书 docx block 数组"""
    text = strip_frontmatter(text)
    lines = text.split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        s = line.strip()
        if not s:
            i += 1
            continue

        # 标题 # ~ ######
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            name = f"heading{level}"
            blocks.append({"block_type": BT_HEADING[level - 1], name: {"elements": inline_elements(m.group(2)), "style": {}}})
            i += 1
            continue

        # 代码块 ``` ```
        if s.startswith("```"):
            code = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # 跳过收尾 ```
            blocks.append({"block_type": BT_CODE, "code": {"elements": [run_elem("\n".join(code))], "style": {"language": 1}}})
            continue

        # 分割线 --- *** ___
        if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", s):
            blocks.append({"block_type": BT_DIVIDER, "divider": {}})
            i += 1
            continue

        # 引用 >  （每行一个引用块，避免嵌套结构）
        if s.startswith(">"):
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].strip()[1:].strip()
                blocks.append({"block_type": BT_QUOTE, "quote": {"elements": inline_elements(q), "style": {}}})
                i += 1
            continue

        # 无序列表
        m = re.match(r"^[-*+]\s+(.*)$", s)
        if m:
            blocks.append({"block_type": BT_BULLET, "bullet": {"elements": inline_elements(m.group(1)), "style": {}}})
            i += 1
            continue

        # 有序列表
        m = re.match(r"^\d+[.、)]\s+(.*)$", s)
        if m:
            blocks.append({"block_type": BT_ORDERED, "ordered": {"elements": inline_elements(m.group(1)), "style": {}}})
            i += 1
            continue

        # 本地图片 ![[xx]] / ![alt](url) → 占位文字（朋友圈配图本人负责）
        if re.match(r"^!\[\[.*\]\]$|^!\[.*\]\(.*\)$", s):
            blocks.append(text_block([run_elem("【图：见本地笔记】")]))
            i += 1
            continue

        # 普通段落
        blocks.append(text_block(inline_elements(line)))
        i += 1

    return blocks


# ---------------------------------------------------------------------------
# 飞书客户端
# ---------------------------------------------------------------------------
class FeishuClient:
    def __init__(self, app_id, app_secret, refresh_token=""):
        self.app_id = app_id
        self.app_secret = app_secret
        self.refresh_token = refresh_token
        self.token = None

    def _refresh_user_token(self):
        """用 refresh_token 换新的 user_access_token，并持久化轮换后的 refresh_token"""
        r = requests.post(
            f"{BASE}/authen/v2/oauth/token",
            json={
                "grant_type": "refresh_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "refresh_token": self.refresh_token,
            },
            timeout=30,
        )
        d = r.json()
        if d.get("code") != 0:
            raise FeishuError(f"刷新用户 token 失败：{d.get('msg')}（授权可能过期，跑一次 reauthorize.py）")
        new_refresh = d.get("refresh_token", "")
        if new_refresh and new_refresh != self.refresh_token:
            self.refresh_token = new_refresh
            # 写回配置，避免下次用旧的失效 token
            try:
                with open(FEISHU_CFG, encoding="utf-8") as f:
                    fcfg = json.load(f)
                fcfg.setdefault("feishu", {})["refresh_token"] = new_refresh
                with open(FEISHU_CFG, "w", encoding="utf-8") as f:
                    json.dump(fcfg, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return d.get("access_token", "")

    def get_token(self):
        # 优先用用户身份（能建知识库、文档全归用户）；没有 refresh_token 才退回应用身份
        if self.refresh_token:
            self.token = self._refresh_user_token()
            return self.token
        r = requests.post(
            f"{BASE}/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
            timeout=30,
        )
        d = r.json()
        if d.get("code") != 0:
            raise FeishuError(f"获取 token 失败：{d.get('msg')}")
        self.token = d["tenant_access_token"]
        return self.token

    def _headers(self):
        if not self.token:
            self.get_token()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _check(self, d, action):
        code = d.get("code")
        if code not in (0, None):
            raise FeishuError(f"{action}失败：code={code} msg={d.get('msg')}")

    # -- 知识库 -------------------------------------------------------------
    def list_spaces(self):
        out, page_token = [], ""
        while True:
            url = f"{BASE}/wiki/v2/spaces?page_size=50"
            if page_token:
                url += f"&page_token={page_token}"
            r = requests.get(url, headers=self._headers(), timeout=30)
            d = r.json()
            self._check(d, "获取知识库列表")
            items = d.get("data", {}).get("items", []) or []
            out.extend(items)
            if not d.get("data", {}).get("has_more"):
                break
            page_token = d["data"]["page_token"]
        return out

    def find_space(self, name):
        for sp in self.list_spaces():
            if sp.get("name") == name:
                return sp
        return None

    def create_node(self, space_id, title):
        r = requests.post(
            f"{BASE}/wiki/v2/spaces/{space_id}/nodes",
            headers=self._headers(),
            json={"obj_type": "docx", "node_type": "origin", "title": title},
            timeout=30,
        )
        d = r.json()
        self._check(d, f"创建节点「{title}」")
        node = d["data"]["node"]
        return node["node_token"], node["obj_token"]

    # -- 文档写入 -------------------------------------------------------------
    def get_root_children(self, doc_id):
        """获取文档根块下现有子块 id 列表（用于计算删除范围）"""
        page_token = ""
        while True:
            url = f"{BASE}/docx/v1/documents/{doc_id}/blocks?page_size=500"
            if page_token:
                url += f"&page_token={page_token}"
            r = requests.get(url, headers=self._headers(), timeout=30)
            d = r.json()
            self._check(d, "获取文档块")
            for b in d.get("data", {}).get("items", []) or []:
                if b.get("block_type") == 1:  # 页面根块
                    return b.get("children", []) or []
            if not d.get("data", {}).get("has_more"):
                break
            page_token = d["data"]["page_token"]
        return []

    def clear_children(self, doc_id):
        """清空文档正文（根块下所有子块）"""
        children = self.get_root_children(doc_id)
        n = len(children)
        if n == 0:
            return 0
        r = requests.delete(
            f"{BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children/batch_delete",
            headers=self._headers(),
            json={"start_index": 0, "end_index": n},
            timeout=30,
        )
        d = r.json()
        self._check(d, "清空旧内容")
        return n

    def append_blocks(self, doc_id, blocks):
        """把块写入文档（root 块 id 即 document_id），分块防超限"""
        for i in range(0, len(blocks), CHUNK):
            part = blocks[i:i + CHUNK]
            r = requests.post(
                f"{BASE}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
                headers=self._headers(),
                json={"children": part},
                timeout=60,
            )
            d = r.json()
            self._check(d, f"写入内容块 {i + 1}~{i + len(part)}")
            time.sleep(WRITE_INTERVAL)


# ---------------------------------------------------------------------------
# 同步逻辑
# ---------------------------------------------------------------------------
def resolve_vault_path(cfg, p):
    if os.path.isabs(p):
        return p
    root = cfg.get("vault_root") or VAULT_ROOT
    return os.path.join(root, p)


def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_files(cfg):
    """返回 [(md绝对路径, 飞书节点标题)]"""
    files = []

    src = cfg.get("source_dir", "00-灵感库（标记灵感）/朋友圈文案库")
    src = resolve_vault_path(cfg, src)
    if os.path.isdir(src):
        for fn in sorted(os.listdir(src)):
            if not fn.endswith(".md"):
                continue
            if fn == "index.md":
                continue
            files.append((os.path.join(src, fn), fn[:-4]))

    for e in cfg.get("extra_entries", []) or []:
        p = resolve_vault_path(cfg, e.get("path", ""))
        if os.path.exists(p):
            title = e.get("title") or os.path.splitext(os.path.basename(p))[0]
            files.append((p, title))

    return files


def sync_file(client, space_id, md_path, title, state, dry_run):
    key = os.path.abspath(md_path)
    mtime = os.path.getmtime(md_path)
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
    blocks = md_to_blocks(content)

    entry = state.get(key)
    if dry_run:
        action = "更新" if entry else "新建"
        return f"将{action}「{title}」({len(blocks)} 块)"

    if entry:
        client.clear_children(entry["obj_token"])
        client.append_blocks(entry["obj_token"], blocks)
        entry["mtime"] = mtime
        return f"已更新「{title}」({len(blocks)} 块)"

    node_token, obj_token = client.create_node(space_id, title)
    client.append_blocks(obj_token, blocks)
    state[key] = {
        "title": title,
        "node_token": node_token,
        "obj_token": obj_token,
        "mtime": mtime,
    }
    return f"已新建「{title}」({len(blocks)} 块)"


def main():
    ap = argparse.ArgumentParser(description="朋友圈文案库 → 飞书知识库 自动同步")
    ap.add_argument("--config", default=os.path.join(SCRIPT_DIR, "config.json"), help="配置文件路径")
    ap.add_argument("--list-spaces", action="store_true", help="列出当前应用可见的知识库")
    ap.add_argument("--dry-run", action="store_true", help="只预览，不真正写入飞书")
    ap.add_argument("--space", help="知识库名称，覆盖 config 里的 wiki_space_name")
    ap.add_argument("--source", help="文案库目录，覆盖 config 里的 source_dir")
    args = ap.parse_args()

    cfg = load_config(args.config)
    app_id = cfg.get("app_id", "")
    app_secret = cfg.get("app_secret", "")
    refresh_token = ""

    # 兜底：自动复用「飞书录音同步」已有的应用（不用手动填凭据）
    if (not app_id or app_id.startswith("你的")) or (not app_secret or app_secret.startswith("你的")):
        if os.path.exists(FEISHU_CFG):
            try:
                with open(FEISHU_CFG, encoding="utf-8") as f:
                    fcfg = json.load(f).get("feishu", {})
                app_id = fcfg.get("app_id", "") or app_id
                app_secret = fcfg.get("app_secret", "") or app_secret
                refresh_token = fcfg.get("refresh_token", "")
            except Exception:
                pass

    if not app_id or not app_secret or app_id.startswith("你的") or app_secret.startswith("你的"):
        print("⚠️  缺少飞书应用凭据。")
        print(f"   已尝试读取 {FEISHU_CFG} 但没找到。")
        print("   手动在 config.json 填 App ID / App Secret，见「接入指引.md」。")
        sys.exit(1)

    client = FeishuClient(app_id, app_secret, refresh_token)
    try:
        client.get_token()
        print("✅ token 获取成功")
    except FeishuError as e:
        print(f"❌ {e}")
        if refresh_token:
            print("   授权可能过期，跑一次：python3 reauthorize.py")
        else:
            print("   检查 config.json 里的 App ID / App Secret 是否正确。")
        sys.exit(1)

    space_name = args.space or cfg.get("wiki_space_name", "朋友圈文案库")

    if args.list_spaces:
        try:
            print("当前应用可见的知识库：")
            for sp in client.list_spaces():
                print(f"  · {sp.get('name')}  ({sp.get('space_id')})")
        except FeishuError as e:
            print(f"❌ {e}")
            print("   通常是权限没开，或机器人没被加进知识库成员。见「接入指引.md」第 3、6 步。")
        return

    space = client.find_space(space_name)
    if not space:
        print(f"❌ 没找到知识库「{space_name}」。")
        print("   请先在飞书创建一个同名知识库，并把机器人加成管理员；")
        print("   或先跑 --list-spaces 看看实际有哪些。")
        sys.exit(1)
    space_id = space["space_id"]
    print(f"✅ 定位知识库：{space['name']} ({space_id})")

    files = collect_files(cfg)
    if not files:
        print("⚠️  文案库里还没有内容（没有 PYQ-*.md）。")
        print("   生成朋友圈文案后再跑一次本脚本即可。")
        return

    state_path = os.path.join(SCRIPT_DIR, ".sync_state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as f:
            state = json.load(f)

    print(f"\n{'[预览模式 DRY RUN] ' if args.dry_run else ''}待同步 {len(files)} 个文件：")
    for md_path, title in files:
        try:
            print("  · " + sync_file(client, space_id, md_path, title, state, args.dry_run))
        except FeishuError as e:
            print(f"  ✗ {e}")

    if not args.dry_run:
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 同步完成，状态记录已保存 → {state_path}")
        print("   手机上：飞书 App 打开「朋友圈文案库」知识库，或微信里点知识库链接。")


if __name__ == "__main__":
    main()
