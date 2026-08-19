# 🖼️ Google Image 出图工具（小红书/公众号配图）

> 替代豆包出图的小红书/公众号配图工具。用 Google Imagen 3 / Gemini 2.5 Flash Image。

## 一、获取 API Key（只需一次）

1. **开代理**（mojie.app，选和 Google 同区域节点）
2. 用**自己的 Google 账号**登录（⚠️ 别用共享账号，Key 绑共享账号有风控风险）
3. 打开 → [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
4. 点 **Create API key** → 选/新建一个 Cloud 项目
5. 进入该 Cloud 项目 → **绑定结算方式**（Billing，图片模型需要付费）→ 启用 **Generative Language API**
6. 复制 Key → 粘贴到本目录 `.env`（参照 `.env.example`）

> 图片模型（Imagen 3）无免费层，首次需绑卡。约 ¥0.03-0.1/张，比豆包 token 成本低且质量更可控。

## 二、用法

```bash
# 小红书竖图封面（默认 9:16）
python3 gen_img.py --prompt "暖色调医养风格，干净明亮，主题...，画面留白，无文字" --size 9:16 --out /tmp/xhs_cover.jpg

# 公众号插图（16:9）
python3 gen_img.py --prompt "..." --size 16:9 --out /tmp/gzh_img.jpg

# 用 Gemini 2.5 Flash Image（真实感最强）
python3 gen_img.py --prompt "..." --model gemini-2.5-flash-image --size 1:1 --out /tmp/img.jpg
```

## 三、接入说明

- 小红书/公众号出图时，我会用本工具替换/补充豆包。
- 输出图片后存到对应笔记的附件目录，Obsidian 里 `![[图片名]]` 直接引用。

## 四、常见问题

| 问题 | 处理 |
|------|------|
| 报错 403 / 无权限 | Key 没绑 Billing 或 Generative Language API 未启用 |
| 报错 429 | 额度/限流，稍等再试 |
| 提示"该账号受限" | 代理节点问题，切换节点后重试 |
