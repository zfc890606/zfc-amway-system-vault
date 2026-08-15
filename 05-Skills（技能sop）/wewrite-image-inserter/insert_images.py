#!/usr/bin/env python3
"""
微信公众号文章图片插入工具

从 张大侠讲师照片 目录随机选取 3-6 张照片，复制到临时目录（纯英文路径），
用 <img> 标签插入文章 markdown。wewrite publish 会自动上传到微信 CDN。

注意事项：
  - 使用 <img> 标签而非 ![]() 语法：因为 converter 的 CJK 间距修正会
    在中英文混写的路径中插入空格，导致文件找不到。
  - 图片先复制到 /tmp/wx-images/（纯英文路径），绕过 CJK 间距修正。
  - 封面图也会同步复制到临时目录，返回封面路径供 publish 使用。

用法：
    python3 insert_images.py <article.md> [--pick-cover]
    --pick-cover  只输出封面路径（给 wewrite publish 的 --cover 参数），不插图

输出：
    - 直接修改 article.md，插入 <img> 标签
    - 打印推荐封面路径
"""

import sys
import os
import random
import re
import shutil

# 照片目录
PHOTO_DIR = os.path.expanduser(
    "~/Documents/zfc最强大脑/02-Areas（调用的知识）/03-短视频系统/张大侠讲师照片"
)

# 临时图片目录（纯英文路径，绕过 converter 的 CJK 间距修正）
TEMP_IMAGE_DIR = "/tmp/wx-images"

# 支持的图片格式
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

# 每篇文章插入的图片数量（随机 3-6 张）
MIN_IMAGES = 3
MAX_IMAGES = 6


def ensure_temp_dir():
    """确保临时图片目录存在"""
    os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)


def get_photo_files():
    """获取照片目录中所有图片文件的绝对路径"""
    if not os.path.isdir(PHOTO_DIR):
        print(f"❌ 照片目录不存在: {PHOTO_DIR}", file=sys.stderr)
        return []

    files = []
    for f in os.listdir(PHOTO_DIR):
        if f.lower().endswith(IMAGE_EXTENSIONS):
            files.append(os.path.join(PHOTO_DIR, f))

    if not files:
        print(f"⚠️ 照片目录中没有找到图片文件", file=sys.stderr)
        return []

    return sorted(files)


def copy_to_temp(photo_files, count):
    """
    随机选 count 张图片，复制到临时目录，返回 (temp_paths, selected_originals)

    文件名用 img1.jpg, img2.jpg ... 确保纯英文路径。
    """
    selected = random.sample(photo_files, min(count, len(photo_files)))
    ensure_temp_dir()

    temp_paths = []
    for i, src_path in enumerate(selected, 1):
        ext = os.path.splitext(src_path)[1].lower()
        # 统一转 .jpg
        dst_name = f"img{i}.jpg"
        dst_path = os.path.join(TEMP_IMAGE_DIR, dst_name)
        shutil.copy2(src_path, dst_path)
        temp_paths.append(dst_path)

    return temp_paths, selected


def find_insertion_points(content):
    """
    查找自然的图片插入点。

    策略：
    1. 每个 ## 段落之间插 1 张
    2. 如果段落数不够，在段落间隙（空行处）均匀分布
    """
    lines = content.split('\n')

    # 找所有 ## 标题的位置（不含 # 一级标题）
    heading_positions = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('## ') and not stripped.startswith('### '):
            heading_positions.append(i)

    # 如果没有二级标题，找段落间的空行
    if not heading_positions:
        paragraph_breaks = []
        for i in range(1, len(lines)):
            if lines[i].strip() == '' and lines[i-1].strip() != '':
                if i > 1 and lines[i-2].strip() == '':
                    continue
                paragraph_breaks.append(i)
        return paragraph_breaks

    return heading_positions


def insert_images(article_path, photo_files, output_path=None):
    """
    在文章 markdown 中插入 <img> 标签。

    先把图片复制到临时目录（纯英文路径），然后用 <img> 标签插入。
    """
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 获取插入点
    insertion_points = find_insertion_points(content)

    # 决定实际要插入的图片数量
    num_to_insert = min(random.randint(MIN_IMAGES, MAX_IMAGES), len(photo_files))
    if num_to_insert < MIN_IMAGES:
        num_to_insert = min(len(photo_files), MIN_IMAGES)

    if num_to_insert == 0:
        print("⚠️ 没有足够的图片可插入", file=sys.stderr)
        return False

    # 复制图片到临时目录
    temp_paths, selected = copy_to_temp(photo_files, num_to_insert)
    num_to_insert = len(temp_paths)

    # 从插入点中均匀选 num_to_insert 个位置
    if len(insertion_points) >= num_to_insert:
        step = len(insertion_points) / num_to_insert
        chosen_indices = [int(i * step) for i in range(num_to_insert)]
        chosen_points = [insertion_points[i] for i in chosen_indices]
    else:
        chosen_points = insertion_points[:]
        lines = content.split('\n')
        extra_positions = [int(len(lines) * p) for p in [0.6, 0.75, 0.9]]
        for pos in extra_positions:
            if len(chosen_points) >= num_to_insert:
                break
            if pos not in chosen_points:
                chosen_points.append(pos)
        chosen_points = chosen_points[:num_to_insert]

    # 按行号逆序排序（从后往前插入，避免行号偏移）
    chosen_points.sort(reverse=True)

    lines = content.split('\n')
    for i, pos in enumerate(chosen_points):
        img_path = temp_paths[i] if i < len(temp_paths) else temp_paths[-1]

        # 用 <img> 标签而非 ![]() 语法
        # ![]() 会被 converter 的 CJK 间距修正破坏路径
        img_html = f'\n\n<img src="{img_path}" />\n'

        insert_at = min(pos, len(lines))
        lines.insert(insert_at, img_html)

    modified = '\n'.join(lines)

    # 写入
    target = output_path or article_path
    with open(target, 'w', encoding='utf-8') as f:
        f.write(modified)

    print(f"✅ 已插入 {num_to_insert} 张图片到: {target}")
    print(f"   临时目录（纯英文路径）: {TEMP_IMAGE_DIR}")
    for i, img_path in enumerate(temp_paths):
        print(f"   {i+1}. {os.path.basename(selected[i])} → {os.path.basename(img_path)}")

    return True


def pick_and_copy_cover(photo_files):
    """随机选一张封面图，复制到临时目录，返回（封面路径，文件名）"""
    if not photo_files:
        return None, None
    cover_src = random.choice(photo_files)
    ensure_temp_dir()
    cover_dst = os.path.join(TEMP_IMAGE_DIR, "cover.jpg")
    shutil.copy2(cover_src, cover_dst)
    return cover_dst, os.path.basename(cover_src)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 insert_images.py <article.md>")
        print("       python3 insert_images.py <article.md> --pick-cover")
        sys.exit(1)

    article_path = sys.argv[1]
    pick_cover_only = "--pick-cover" in sys.argv

    if not os.path.isfile(article_path):
        print(f"❌ 文章文件不存在: {article_path}", file=sys.stderr)
        sys.exit(1)

    photo_files = get_photo_files()
    if not photo_files:
        print("❌ 没有找到可用图片", file=sys.stderr)
        sys.exit(1)

    print(f"📸 照片库: {len(photo_files)} 张可用图片")

    if pick_cover_only:
        cover_path, cover_name = pick_and_copy_cover(photo_files)
        if cover_path:
            print(f"🖼️ 封面路径: {cover_path}")
            print(f"   原始文件: {cover_name}")
        return

    success = insert_images(article_path, photo_files)
    if not success:
        sys.exit(1)

    # 输出封面推荐
    cover_path, cover_name = pick_and_copy_cover(photo_files)
    if cover_path:
        print(f"\n🖼️ 封面已复制: {cover_path}")
        print(f"   原始文件: {cover_name}")


if __name__ == "__main__":
    main()
