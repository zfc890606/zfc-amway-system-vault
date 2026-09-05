#!/usr/bin/env python3
"""
排序 AI选题库.md — 三个分类表按频率从高到低排列
"""

import re

FILE = "/Users/mac/Documents/zfc最强大脑/00-灵感库（标记灵感）/AI选题库.md"

def freq_score(text):
    t = text.strip().replace('**', '')
    stars = t.count('⭐')
    if '极高' in t: return 500
    if '很高' in t: return 400
    if '高' in t: return 310
    if '中高' in t: return 300
    if '中' in t: return 200
    if '低' in t: return 100
    return stars * 90

def is_separator(line):
    """检测 Markdown 表格分隔行 (| :-: | --- | 等)"""
    return bool(re.match(r'^\|[-:\s]+(\|[-:\s]+)*\|\s*$', line))

def is_header(line):
    """检测表格表头行"""
    return '|' in line and ('优先级' in line or '选题' in line or '频率' in line)

def is_empty_or_comment(line):
    s = line.strip()
    return s == '' or s.startswith('>') or s.startswith('---')

def main():
    with open(FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到所有分类表格区域
    # 特征: ### 分类X 标题 → 接下来有表格
    sections = []
    for i, line in enumerate(lines):
        if line.startswith('## ') and '分类' in line:
            sections.append(i)

    print(f"找到 {len(sections)} 个分类区域")

    # 对每个分类区域处理
    for si, sec_start in enumerate(sections):
        # 找到该区域的结束（下一个 ### 或文件结尾）
        if si + 1 < len(sections):
            sec_end = sections[si + 1]
        else:
            sec_end = len(lines)

        section_lines = lines[sec_start:sec_end]
        section_name = section_lines[0].strip()
        print(f"\n处理: {section_name}")

        # 在这个区域内找表格
        # 找表头、分隔行、数据行
        tbl_start = None
        for j, line in enumerate(section_lines):
            if line.startswith('|') and ('优先级' in line or '选题' in line):
                tbl_start = sec_start + j
                break

        if tbl_start is None:
            print("  未找到表格")
            continue

        # 计算在全局lines中的偏移
        offset = sec_start

        # 找表格行
        data_rows = []
        for j in range(tbl_start - offset, len(section_lines)):
            line = section_lines[j]
            if is_separator(line):
                continue
            if line.startswith('|') and not is_header(line):
                # 数据行
                cells = [c.strip() for c in line.strip().split('|')]
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                if len(cells) >= 3:
                    freq = cells[2]  # 频率在第3列
                    data_rows.append((offset + j, line, cells, freq))

        if not data_rows:
            print("  未找到数据行")
            continue

        print(f"  找到 {len(data_rows)} 条数据")

        # 排序: 按频率从高到低
        def sort_key(item):
            _, _, _, freq = item
            return -freq_score(freq)

        sorted_rows = sorted(data_rows, key=sort_key)

        # 替换行
        old_indices = [r[0] for r in data_rows]
        new_lines = [r[1] for r in sorted_rows]

        # 替换
        for idx, new_line in zip(old_indices, new_lines):
            lines[idx] = new_line

        print(f"  排序完成")

    # 写回
    with open(FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print(f"\n✅ AI选题库 排序完成！")

if __name__ == '__main__':
    main()
