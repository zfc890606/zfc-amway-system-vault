---
type: tool
tool: social-auto-upload
分类: 内容发布类
安装日期: 2026-08-19
状态: ✅ 已安装可用
上游: https://github.com/dreammis/social-auto-upload
---

# 📤 social-auto-upload — 多平台视频自动发布

> 一键把短视频/图文自动发布到 **抖音 / B站 / 小红书 / 快手 / 视频号 / YouTube** 等平台，支持定时发布。
> 本项目是"自媒体输出"流水线的**最后一环**：脚本写完 → 剪出成片 → `sau` 直接发布。

## 📍 安装位置

- **程序本体**：`social-auto-upload/`（本目录，Python 3.12 venv + patchright 浏览器驱动）
- **Claude Code skills**（已装到 `~/.claude/skills/`，重启会话后自动可用）：
  - `douyin-upload` · `bilibili-upload` · `kuaishou-upload` · `xiaohongshu-upload`
- **CLI 入口**：`sau` 命令已软链到 `~/.local/bin/sau`，任意目录可直接调用

## 🚀 快速使用

```bash
# 1) 先登录平台账号（生成 cookie，一个 account_name = 一个账号）
sau douyin login --account 我的抖音
sau xiaohongshu login --account 小红书1

# 2) 校验 cookie 是否有效
sau douyin check --account 我的抖音

# 3) 发视频（title + desc + tags）
sau douyin upload-video --account 我的抖音 --file 视频.mp4 --title "标题" --desc "简介" --tags "标签1,标签2"

# 4) 发图文（title + note + tags）
sau xiaohongshu upload-note --account 小红书1 --images 图1.png 图2.png --title "标题" --note "正文"
```

| 平台 | 命令前缀 | 支持 | 备注 |
|------|---------|------|------|
| 抖音 | `sau douyin` | 视频/图文 | 短信二次验证时写 `verify_code.txt` |
| B站 | `sau bilibili` | 视频 | 登录建议本人在本地终端扫码 |
| 小红书 | `sau xiaohongshu` | 视频/图文 | 旧流程需 `XHS_SERVER` |
| 快手 | `sau kuaishou` | 视频/图文 | |
| 视频号 | `sau tencent` | 视频 | |
| YouTube | `sau youtube` | 视频 | 交互式 Google 登录，被墙地区配 `YT_PROXY` |

**登录二维码**：登录时若生成本地二维码图片，直接打开仓库目录下的 `qrcode.png` 扫码。

## ⚙️ 配置说明（conf.py）

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `LOCAL_CHROME_PATH` | 本机 Google Chrome | 用真实浏览器更隐蔽，降低平台检测风险 |
| `LOCAL_CHROME_HEADLESS` | `True` | 无头模式（适合 CLI/自动化） |
| `DEBUG_MODE` | `True` | 调试输出 |
| `YT_PROXY` | `None` | YouTube 代理，被墙地区填 `http://127.0.0.1:7890` |

## 🔄 更新方法

```bash
cd "social-auto-upload" && git pull && uv pip install -e . && patchright install chromium
```

## 📚 参考文档（都在程序目录 docs/ 和 skills/ 里）

- 安装：`docs/install.md` ｜ CLI 用法：`docs/CLI.md` ｜ 更新：`docs/update.md`
- 各平台 skill：`~/.claude/skills/{平台}-upload/`（含 CLI 契约、故障排查）

## ⚠️ 注意

- **账号安全**：`--account` 对应本地 cookie 文件，多个账号用不同名字隔离
- **B站登录**：CLI 不要求手动装 biliup（自动下载），登录二维码在本地终端扫
- **定时发布**：只在用户明确要求时才用 `--schedule "YYYY-MM-DD HH:MM"`，默认立即发布
- **合规**：发布内容仍走本 vault 的医疗合规 + 违规解密质检，平台只负责"发"这一步
