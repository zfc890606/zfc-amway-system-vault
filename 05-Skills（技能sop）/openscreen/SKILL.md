---
name: openscreen
description: 免费开源录屏工具，Screen Studio 替代品。支持窗口/全屏录制、麦克风+系统音频、摄像头画中画、自动跟随缩放、鼠标特效、自动字幕（离线）、剪辑/标注/GIF 导出。适合录制产品演示、操作教程、短视频。
tags: [录屏, 短视频工具, 开源, demo, 教程录制]
---

# OpenScreen — 免费开源录屏工具

> **一句话**：免费开源的 Screen Studio 替代品，适合录制产品演示、操作教程和短视频素材。

OpenScreen 是一款 **100% 免费、开源** 的屏幕录制和演示制作工具。MIT 协议，个人和商用皆可。没有水印、没有付费墙、没有功能限制。

- GitHub：<https://github.com/getopenscreen/openscreen>
- 当前版本：**v1.6.0**（2026-07-05 发布）
- 平台：macOS（ARM64 / x64）、Windows、Linux
- 语言：支持简体中文

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **屏幕录制** | 录制单个窗口或全屏 |
| **音频录制** | 麦克风 + 系统音频（macOS 13+） |
| **摄像头画中画** | 拖拽定位、镜像、形状选择 |
| **自动缩放** | 跟随鼠标自动缩放，可调深度/时长/缓动 |
| **手动缩放** | 像素级精确缩放定位 |
| **鼠标特效** | 自定义大小、平滑、点击效果、主题皮肤、路径平滑 |
| **自动字幕** | 设备端离线生成语音字幕 |
| **背景替换** | 壁纸、纯色、渐变、自定义图片 |
| **运动模糊** | 让缩放过渡更流畅 |
| **剪辑编辑** | 裁剪、修剪、分段变速、时间轴吸附、音频波形 |
| **标注工具** | 文字、箭头、图片标注，含文字动画预设 |
| **导出** | MP4 或 GIF，多种宽高比和分辨率 |
| **快捷键** | 全部可自定义 |

---

## 安装

### macOS（Apple Silicon / Intel）

1. 下载最新 DMG 安装包（选 arm64 或 x64）：
   - **ARM64（M1/M2/M3/M4）**：<https://github.com/getopenscreen/openscreen/releases/download/v1.6.0/Openscreen-Mac-arm64-1.6.0.dmg>
   - **Intel**：<https://github.com/getopenscreen/openscreen/releases/download/v1.6.0/Openscreen-Mac-x64-1.6.0.dmg>

2. 打开 DMG，将 OpenScreen 拖入 `/Applications`

3. 如果 Gatekeeper 阻止运行，终端执行：
   ```bash
   xattr -rd com.apple.quarantine /Applications/Openscreen.app
   ```

4. 前往 **系统设置 > 隐私与安全性**，授予：
   - **屏幕录制** 权限
   - **辅助功能** 权限
   - （macOS 14.2+ 还需要音频捕获权限）

### Windows

```bash
winget install OpenScreen
```
或下载 `.exe` 安装包。

### Linux

```bash
# Debian/Ubuntu
sudo apt install ./Openscreen-Linux-latest.deb

# Arch/Manjaro
sudo pacman -U Openscreen-Linux-latest.pacman

# AppImage（任意发行版）
chmod +x Openscreen-Linux-*.AppImage
./Openscreen-Linux-*.AppImage
```

---

## 使用提示

### 录制流程
1. 选择录制窗口或全屏
2. 选择音频输入（麦克风 + 系统音频）
3. 开启摄像头画中画（可选）
4. 点击录制 — 自动/手动缩放会在后期编辑中生效
5. 录制完成后进入编辑器

### 编辑器功能
- **时间轴**：修剪片段、调整速度、添加标注
- **缩放**：添加自动跟随缩放或手动缩放关键帧
- **字幕**：一键生成离线语音字幕
- **背景**：更换背景、壁纸、纯色
- **导出**：选择 MP4 或 GIF，调整分辨率和宽高比

### 快捷键
在设置中可自定义全部快捷键。默认常用：
- `⌘R` — 开始/停止录制
- `Space` — 播放/暂停
- `⌘S` — 导出

---

## 在短视频创作管线中的位置

OpenScreen 适合在以下场景使用：

```
┌─ 短视频流水线 ──────────────────────────┐
│                                          │
│  OpenScreen（录制素材）                    │
│    ↓                                     │
│  剪辑工具（修剪/配音/字幕）                │
│    ↓                                     │
│  发布（视频号/小红书/公众号）              │
│                                          │
└──────────────────────────────────────────┘
```

**典型场景**：
- **操作演示**：录制 App 操作 → 加缩放和标注 → 导出 → 发短视频
- **产品展示**：录制网页/软件界面 → 加摄像头画中画 → 加字幕 → 导出
- **教程制作**：分步骤录制 → 剪辑分段 → 加文字说明 → GIF/MP4 输出

---

## 相关链接

- GitHub 仓库：<https://github.com/getopenscreen/openscreen>
- 发布页面（下载）：<https://github.com/getopenscreen/openscreen/releases>
- Discord 社区：<https://discord.gg/VvT6Vtnyh>
- 路线图：<https://github.com/getopenscreen/openscreen/blob/main/ROADMAP.md>
- 许可证：MIT — 100% 免费，个人和商用
