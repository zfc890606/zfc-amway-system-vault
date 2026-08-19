#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Image 出图工具（小红书 / 公众号配图）
=============================================
依赖：google-genai（已安装）
用法：
  python3 gen_img.py --prompt "你的提示词" [--model imagen-3.0-generate-002] [--size 9:16] [--out out.jpg]

模型选择：
  imagen-3.0-generate-002  -> 干净、写实、中文文字渲染好（推荐小红书封面/配图·医养风）
  gemini-2.5-flash-image   -> 真实感最强、支持对话式修改（Nano Banana）

Key 读取顺序：环境变量 GEMINI_API_KEY -> 本目录 .env 文件
"""
import argparse
import os
import pathlib
import sys


def load_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    env_path = pathlib.Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Google Image 出图工具")
    parser.add_argument("--prompt", required=True, help="图片描述提示词")
    parser.add_argument(
        "--model",
        default="imagen-3.0-generate-002",
        choices=["imagen-3.0-generate-002", "gemini-2.5-flash-image"],
        help="生成模型（默认 imagen-3.0-generate-002）",
    )
    parser.add_argument(
        "--size",
        default="9:16",
        help="画幅比例：9:16（小红书竖图）/ 1:1 / 4:3 / 16:9（默认 9:16）",
    )
    parser.add_argument("--out", default="out.jpg", help="输出图片路径")
    args = parser.parse_args()

    key = load_key()
    if not key:
        sys.exit(
            "❌ 未找到 GEMINI_API_KEY。\n"
            "   1) 在 Google AI Studio 申请 API Key（https://aistudio.google.com/apikey）\n"
            "   2) 复制到本目录 .env 文件（参照 .env.example），或设环境变量 GEMINI_API_KEY"
        )

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.model == "imagen-3.0-generate-002":
        result = client.models.generate_images(
            model=args.model,
            prompt=args.prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=args.size,
                output_mime_type="image/jpeg",
            ),
        )
        img = result.generated_images[0].image.image_bytes
    else:  # gemini-2.5-flash-image
        result = client.models.generate_content(
            model=args.model,
            contents=[args.prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(aspect_ratio=args.size),
            ),
        )
        img = None
        for part in result.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                img = part.inline_data.data
                break
        if img is None:
            sys.exit("❌ 模型未返回图片，请检查提示词或模型名称。")

    out_path.write_bytes(img)
    print(f"✅ 图片已生成: {out_path.resolve()}")
    print(f"   画幅: {args.size} | 模型: {args.model}")


if __name__ == "__main__":
    main()
