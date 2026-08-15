#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信微盘(WeDrive)素材读取工具
=================================
功能：读取企业微信微盘里的文件/图片素材列表，并下载到本地。

前提：
1. 已配置 config.json 里的 corpid / corpsecret
2. 该应用已获得"微盘"接口权限
   （企业微信管理后台 → 应用管理 → 自建应用 → 接口授权 → 勾选"微盘"）

用法：
    python3 wedrive_read.py token                     # 测试 token 是否有效
    python3 wedrive_read.py spaces                    # 列出所有微盘空间
    python3 wedrive_read.py files <spaceid> [parentid]  # 列出空间内文件/文件夹
    python3 wedrive_read.py info <fileid>             # 查看文件详情
    python3 wedrive_read.py download <fileid> <保存目录> # 下载文件到本地

接口以企业微信官方文档为准：https://developer.work.weixin.qq.com/document/path/93650
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse

import requests

BASE = "https://qyapi.weixin.qq.com/cgi-bin"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"[错误] 找不到配置文件：{CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    if "你的企业ID" in str(cfg.get("corpid", "")) or "你的应用Secret" in str(cfg.get("corpsecret", "")):
        print("[错误] 请先在 config.json 中填入你的 企业ID 和 应用Secret")
        sys.exit(1)
    return cfg


class WeCom:
    def __init__(self, corpid, corpsecret):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.token = None
        self.token_expire = 0

    def get_token(self):
        """获取 access_token（带 2 小时缓存）"""
        if self.token and time.time() < self.token_expire:
            return self.token
        url = f"{BASE}/gettoken"
        params = {"corpid": self.corpid, "corpsecret": self.corpsecret}
        resp = requests.get(url, params=params, timeout=15).json()
        if resp.get("errcode") != 0:
            print(f"[错误] 获取 token 失败：{resp}")
            sys.exit(1)
        self.token = resp["access_token"]
        self.token_expire = time.time() + resp["expires_in"] - 60
        return self.token

    def api(self, endpoint, body=None):
        """调用 POST 接口"""
        url = f"{BASE}/{endpoint}?access_token={self.get_token()}"
        resp = requests.post(url, json=body or {}, timeout=30).json()
        if resp.get("errcode") != 0:
            print(f"[错误] {endpoint} 失败：{resp}")
            sys.exit(1)
        return resp

    def spaces(self):
        """列出微盘空间"""
        data = []
        cursor = ""
        while True:
            r = self.api("wedrive/space_list", {"cursor": cursor, "limit": 100})
            data.extend(r.get("space_list", []))
            if not r.get("has_more"):
                break
            cursor = r.get("next_cursor", "")
        return data

    def files(self, spaceid, parentid=""):
        """列出空间内文件/文件夹"""
        r = self.api("wedrive/file_list", {
            "spaceid": spaceid,
            "parentid": parentid or "",
            "limit": 100,
        })
        return r.get("file_list", [])

    def file_info(self, fileid):
        return self.api("wedrive/file_info", {"fileid": fileid})

    def download_url(self, fileid):
        return self.api("wedrive/file_download", {"fileid": fileid})


def print_file(f, indent=0):
    kind = "📁 文件夹" if f.get("type") == 3 else "📄 文件"
    size = f.get("size", 0)
    size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/1024/1024:.2f}MB"
    name = f.get("file_name", "")
    fid = f.get("fileid", "")
    print(" " * indent + f"{kind}  {name}  ({size_str})  fileid={fid}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cfg = load_config()
    wc = WeCom(cfg["corpid"], cfg["corpsecret"])
    cmd = sys.argv[1]

    if cmd == "token":
        t = wc.get_token()
        print(f"✅ token 获取成功：{t[:20]}...（有效2小时）")

    elif cmd == "spaces":
        print("📦 微盘空间列表：")
        for s in wc.spaces():
            print(f"  📁 {s.get('space_name')}  spaceid={s.get('spaceid')}")

    elif cmd == "files":
        if len(sys.argv) < 3:
            print("用法：python3 wedrive_read.py files <spaceid> [parentid]")
            sys.exit(1)
        spaceid = sys.argv[2]
        parentid = sys.argv[3] if len(sys.argv) > 3 else ""
        flist = wc.files(spaceid, parentid)
        print(f"📂 文件列表（共{len(flist)}项）：")
        for f in flist:
            print_file(f)

    elif cmd == "info":
        if len(sys.argv) < 3:
            print("用法：python3 wedrive_read.py info <fileid>")
            sys.exit(1)
        print(json.dumps(wc.file_info(sys.argv[2]), ensure_ascii=False, indent=2))

    elif cmd == "download":
        if len(sys.argv) < 4:
            print("用法：python3 wedrive_read.py download <fileid> <保存目录>")
            sys.exit(1)
        fileid = sys.argv[2]
        outdir = sys.argv[3]
        os.makedirs(outdir, exist_ok=True)
        info = wc.file_info(fileid)
        name = info.get("file_name", "download")
        dl = wc.download_url(fileid)
        url = dl.get("download_url")
        if not url:
            print("[错误] 未获取到下载地址")
            sys.exit(1)
        path = os.path.join(outdir, name)
        print(f"⬇️  下载中：{name}")
        urllib.request.urlretrieve(url, path)
        print(f"✅ 已保存：{path}")

    else:
        print(f"未知命令：{cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
