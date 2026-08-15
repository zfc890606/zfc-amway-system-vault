---
name: banana-slides
description: AI 原生 PPT 生成工具 — 从想法、大纲、文档生成可编辑的演示文稿，支持 PPTX/PDF 导出、批量生成、模板控制、对话式编辑。
source: https://github.com/Anionex/banana-slides
tags: [PPT, 演示文稿, AI生成, 幻灯片, 工具]
---

# Banana Slides — AI PPT 生成工具

> 基于 AI 的 PPT 生成应用，从想法/大纲/文档生成可编辑演示文稿。支持提示词生成、模板控制、素材解析、对话式编辑、PPTX 导出。

---

## 环境准备

### 后端启动（本地 Docker）

```bash
git clone https://github.com/Anionex/banana-slides
cd banana-slides
cp .env.example .env
# 编辑 .env — 至少设置一个 AI 供应商密钥
```

然后在 `.env` 中配置 AI 供应商：

```env
# Google Gemini（默认）
AI_PROVIDER_FORMAT=gemini
GOOGLE_API_KEY=你的密钥

# 或 OpenAI 兼容接口
AI_PROVIDER_FORMAT=openai
OPENAI_API_KEY=你的密钥
OPENAI_BASE_URL=https://api.openai.com/v1
```

支持的供应商：`gemini`、`openai`、`vertex`、`lazyllm`、`anthropic`

启动后端（二选一）：

```bash
# 方案 A：Docker 一键启动
docker compose -f docker-compose.allinone.yml up -d

# 方案 B：手动启动
cd backend
uv sync
uv run alembic upgrade head
uv run python app.py
```

验证后端运行：

```bash
curl -sf http://localhost:5011/health
```

### CLI 工具（已安装）

banana-cli 已通过 uv 全局安装：

```bash
banana-cli --help
```

---

## 核心用法

### 完整流程：想法 → PPT

```bash
# 1. 创建项目
result=$(banana-cli --json projects create --creation-type idea --idea-prompt "你的主题")
project_id=$(echo "$result" | jq -r '.data.project_id')
banana-cli projects use "$project_id"

# 2. 一键生成（大纲→描述→图片）
banana-cli workflows full --language zh --pages 8

# 3. 导出本地文件
banana-cli exports pptx --output ./slides.pptx
```

### 设置工作项目（避免重复传 --project-id）

```bash
banana-cli projects use a1b2     # 设置工作项目
banana-cli workflows outline      # 使用工作项目
banana-cli projects use           # 查看当前项目
banana-cli projects unuse         # 清除
```

### 导出格式

```bash
banana-cli exports pptx --output ./slides.pptx
banana-cli exports pdf --output ./report.pdf
banana-cli exports pptx          # 不带 --output 返回下载 URL
```

### 批量生成

```bash
cat > jobs.jsonl << 'EOF'
{"job_id":"t1","job_type":"full_generation","creation_type":"idea","idea_prompt":"AI 入门","language":"zh","export":{"formats":["pptx"]}}
EOF

banana-cli run jobs --file jobs.jsonl --report report.json --state-file state.json
```

### 改造现有 PPT

```bash
banana-cli renovation create --file /绝对/路径/到/slides.pptx --language zh
```

### ⚠️ 字体大小规则（生成 PPTX 时必加）

在 `--extra-requirements` 或 prompt 中必须加入：
- 中文字号不低于 **28pt**，英文标题不低于 **40pt**
- 每页字数控制在最少，确保主体文字在投影上清晰可见

---

## 项目与页面管理

```bash
# 项目操作
banana-cli projects list          # 列出项目
banana-cli projects get a1b2      # 查看项目详情（支持短前缀匹配）
banana-cli projects use a1b2      # 设置工作项目

# 页面操作
banana-cli pages list             # 列出页面
banana-cli pages edit-image --page-id b9c8 --instruction "把标题改成红色"
```

---

## 重要提示

- 文件路径参数（`--file`、`--image`）需要**绝对路径**
- 异步任务（描述生成、图片生成、可编辑导出）**默认等待完成**，显示进度到 stderr
- 加 `--no-wait` 立即返回 task_id
- 配置优先级：CLI 参数 > 环境变量（`BANANA_CLI_*`）> TOML 配置（`~/.config/banana-slides/cli.toml`）> 默认值
- JSON 输出模式：`banana-cli --json projects list | jq '.data.projects[].project_id'`

---

## 参考链接

- GitHub：https://github.com/Anionex/banana-slides
- 文档：https://docs.bananaslides.online/
- CLI 用法详见 `banana-cli --help`
