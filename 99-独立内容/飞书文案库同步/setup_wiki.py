#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性配置：创建「朋友圈文案库」知识库
========================================

    python3 setup_wiki.py

创建知识库只能用「用户身份」的 token，所以脚本会自动：
  1. 用已有应用的 refresh_token 换 user_access_token
  2. 创建知识库「朋友圈文案库」（已存在则跳过）
  3. 输出确认

如果提示授权权限不足，先跑一次：
    python3 reauthorize.py
（打开链接点「同意」即可）
"""

import json
import os
import sys

import requests

BASE = "https://open.feishu.cn/open-apis"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FEISHU_CFG = os.path.expanduser("~/.config/feishu-obsidian/config.json")
SPACE_NAME = "朋友圈文案库"


def log(msg):
    print(msg)


def load_credentials():
    if os.path.exists(FEISHU_CFG):
        try:
            d = json.load(open(FEISHU_CFG, encoding="utf-8"))
            app_id = d.get("feishu", {}).get("app_id", "")
            app_secret = d.get("feishu", {}).get("app_secret", "")
            refresh_token = d.get("feishu", {}).get("refresh_token", "")
            if app_id and app_secret:
                return app_id, app_secret, refresh_token
        except Exception:
            pass
    own = os.path.join(SCRIPT_DIR, "config.json")
    if os.path.exists(own):
        d = json.load(open(own, encoding="utf-8"))
        app_id, app_secret = d.get("app_id", ""), d.get("app_secret", "")
        if app_id and app_secret and not app_id.startswith("你的"):
            return app_id, app_secret, ""
    return None, None, None


def get_user_token(app_id, app_secret, refresh_token):
    if not refresh_token:
        raise RuntimeError("没有 refresh_token")
    r = requests.post(f"{BASE}/authen/v2/oauth/token", json={
        "grant_type": "refresh_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "refresh_token": refresh_token,
    }, timeout=30)
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"刷新用户 token 失败: {d.get('msg')}（授权可能已过期，跑一次 reauthorize.py）")
    # 飞书每次刷新会轮换 refresh_token，必须存回，否则旧的立即失效
    new_refresh = d.get("refresh_token", "")
    if new_refresh and new_refresh != refresh_token:
        try:
            fcfg = json.load(open(FEISHU_CFG, encoding="utf-8"))
            fcfg.setdefault("feishu", {})["refresh_token"] = new_refresh
            with open(FEISHU_CFG, "w", encoding="utf-8") as f:
                json.dump(fcfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    return d.get("access_token", "")


def find_space(token, name):
    r = requests.get(f"{BASE}/wiki/v2/spaces?page_size=50",
                     headers={"Authorization": f"Bearer {token}"}, timeout=30)
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"获取知识库列表失败: {d.get('msg')}")
    for sp in d.get("data", {}).get("items", []):
        if sp.get("name") == name:
            return sp
    return None


def create_space(token, name):
    r = requests.post(f"{BASE}/wiki/v2/spaces",
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
                      json={"name": name, "description": "朋友圈文案库（自动同步）"}, timeout=30)
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"创建知识库失败: {d.get('msg')}")
    return d.get("data", {}).get("space", {})


def main():
    app_id, app_secret, refresh_token = load_credentials()
    if not app_id:
        log("❌ 找不到应用凭据")
        sys.exit(1)

    log("🔑 用你的身份换取 token...")
    try:
        token = get_user_token(app_id, app_secret, refresh_token)
        log("  ✅ 成功")
    except RuntimeError as e:
        log(f"  ❌ {e}")
        log("\n   你的授权缺少「知识库/写文档」权限，先跑一次：")
        log("   python3 reauthorize.py")
        log("   （会弹链接，点「同意」即可）")
        sys.exit(1)

    log(f"\n📚 检查知识库「{SPACE_NAME}」...")
    try:
        space = find_space(token, SPACE_NAME)
        if space:
            log(f"  ✅ 已存在: {space['space_id']}")
        else:
            log("  未找到，正在创建...")
            space = create_space(token, SPACE_NAME)
            log(f"  ✅ 已创建: {space['space_id']}（归你所有）")
    except RuntimeError as e:
        log(f"  ❌ {e}")
        log("   检查是否已跑过 reauthorize.py 并授权成功。")
        sys.exit(1)

    log(f"\n🎉 配置完成！space_id = {space['space_id']}")
    log("下一步运行同步：python3 sync_pyq_to_feishu.py")


if __name__ == "__main__":
    main()
