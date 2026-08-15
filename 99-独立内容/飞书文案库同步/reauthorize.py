#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书重新授权：给已有应用加上「知识库 + 写文档」权限
====================================================

你的应用之前授权录音同步时只有「只读」权限，现在需要补上写权限。
跑本脚本会弹出一个授权链接，你打开后点「同意/授权」即可。

    python3 reauthorize.py

完成后会自动把新的 refresh_token 存回 ~/.config/feishu-obsidian/config.json，
之后 setup_wiki.py / sync_pyq_to_feishu.py 都会自动用你的身份工作。
"""

import json
import os
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

API_BASE = "https://open.feishu.cn/open-apis"
CONFIG_PATH = os.path.expanduser("~/.config/feishu-obsidian/config.json")

OAUTH_PORT = 9981  # 应用已登记的回调端口（录音同步用的同一个）
OAUTH_REDIRECT_URI = f"http://localhost:{OAUTH_PORT}/callback"
# 全权限：妙记（录音转写）+ 云盘只读 + 文档读写 + 知识库 + 离线刷新
# 妙记权限正确代码：minutes:minutes.search:read（搜索）/ minutes:minutes:readonly（只读）
# / minutes:minutes.transcript:export（导出转写）
OAUTH_SCOPE = ("offline_access drive:drive:readonly docx:document docx:document:readonly "
               "minutes:minutes.search:read minutes:minutes:readonly minutes:minutes.transcript:export "
               "wiki:wiki")


class Handler(BaseHTTPRequestHandler):
    code = None

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query)
        if "code" in q:
            Handler.code = q["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>✅ 授权成功，可以关闭本页面</h1>".encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"no code")
        # 收到回调后立即关闭服务器
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *a):
        pass


def load_app_credentials():
    if os.path.exists(CONFIG_PATH):
        d = json.load(open(CONFIG_PATH, encoding="utf-8"))
        app_id = d.get("feishu", {}).get("app_id", "")
        app_secret = d.get("feishu", {}).get("app_secret", "")
        if app_id and app_secret:
            return app_id, app_secret
    own = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(own):
        d = json.load(open(own, encoding="utf-8"))
        app_id, app_secret = d.get("app_id", ""), d.get("app_secret", "")
        if app_id and app_secret and not app_id.startswith("你的"):
            return app_id, app_secret
    return None, None


def save_refresh_token(refresh_token):
    d = json.load(open(CONFIG_PATH, encoding="utf-8"))
    d.setdefault("feishu", {})["refresh_token"] = refresh_token
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def main():
    app_id, app_secret = load_app_credentials()
    if not app_id:
        print("❌ 找不到应用凭据")
        sys.exit(1)

    auth_url = (
        f"https://accounts.feishu.cn/open-apis/authen/v1/authorize"
        f"?client_id={app_id}"
        f"&redirect_uri={OAUTH_REDIRECT_URI}"
        f"&scope={OAUTH_SCOPE}"
        f"&response_type=code"
    )

    server = HTTPServer(("localhost", OAUTH_PORT), Handler)
    server.timeout = 300

    print("=" * 60)
    print("🔐 请打开下面这个链接，然后点「同意授权」：")
    print()
    print(f"   {auth_url}")
    print()
    print("   等待授权回调（5 分钟内有效）...")
    print("=" * 60)
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server.handle_request()  # 阻塞直到回调或超时
    code = Handler.code
    if not code:
        print("\n❌ 没等到授权回调，请重试。")
        sys.exit(1)

    print("\n📡 收到授权码，正在交换 token...")
    r = requests.post(f"{API_BASE}/authen/v2/oauth/token", json={
        "grant_type": "authorization_code",
        "client_id": app_id,
        "client_secret": app_secret,
        "code": code,
        "redirect_uri": OAUTH_REDIRECT_URI,
    }, timeout=30)
    d = r.json()
    if d.get("code") != 0:
        print(f"❌ token 交换失败: {d.get('msg')}")
        sys.exit(1)

    refresh_token = d.get("refresh_token", "")
    if not refresh_token:
        print("❌ 没拿到 refresh_token")
        sys.exit(1)

    save_refresh_token(refresh_token)
    print("✅ 授权完成！新的权限已保存。")
    print("   下一步：python3 setup_wiki.py")


if __name__ == "__main__":
    main()
