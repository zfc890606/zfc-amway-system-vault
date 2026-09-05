#!/usr/bin/env python3
"""
排序 安利选题库.md — 总榜 + 分榜按频率从高到低排列
"""

import re

FILE = "/Users/mac/Documents/zfc最强大脑/00-灵感库（标记灵感）/安利选题库.md"

# ── 频率评分 ──
def freq_score(text):
    t = text.strip().replace('**', '')
    stars = t.count('⭐')
    if '极高' in t: return (500, stars, t)
    if '很高' in t: return (400, stars, t)
    if '高' in t: return (310, stars, t)
    if '中高' in t: return (300, stars, t)
    if '中' in t: return (200, stars, t)
    if '低' in t: return (100, stars, t)
    return (stars * 90, stars, t)  # fallback

def is_table_row(line):
    """判断是否是表格数据行（非表头、非分隔行）"""
    s = line.strip()
    if not s.startswith('|'): return False
    if re.match(r'^\|[-:\s]+(\|[-:\s]+)*\|\s*$', s): return False  # 分隔行
    if '| 排名' in s or '|排名' in s: return False  # 表头
    return True

def parse_row(line):
    """将表格行拆成单元格列表"""
    cells = [c.strip() for c in line.strip().split('|')]
    if cells and cells[0] == '':
        cells = cells[1:]
    if cells and cells[-1] == '':
        cells = cells[:-1]
    return cells

def main():
    with open(FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # ── 1. 定位主表 ──
    main_start = None
    main_end = None
    for i, line in enumerate(lines):
        if '当前痛点排行榜' in line:
            main_start = i
        if main_start is not None and line.strip() == '---' and i > main_start + 5:
            main_end = i
            break

    print(f"主表范围: {main_start} ~ {main_end}")

    # 在范围内找表格行
    table_indices = [i for i in range(main_start, main_end) if is_table_row(lines[i])]
    print(f"找到 {len(table_indices)} 个表格数据行")

    # 解析数据行
    rows = []
    for idx in table_indices:
        cells = parse_row(lines[idx])
        if len(cells) >= 7:
            rows.append((idx, cells))
        else:
            print(f"  跳过行 {idx}: {len(cells)} cells, {lines[idx][:50]}")

    print(f"解析成功: {len(rows)} 行")

    # ── 2. 排序 ──
    def sort_key(item):
        _, cells = item
        freq = cells[2] if len(cells) > 2 else ''
        return (-freq_score(freq)[0], cells[1])

    sorted_rows = sorted(rows, key=sort_key)

    # ── 3. 建立编号映射 ──
    old_to_new = {}
    for new_rank, (idx, cells) in enumerate(sorted_rows, 1):
        # 从旧行提取旧编号（第一个单元格中的数字）
        old_rank_match = re.search(r'(\d+)', cells[0])
        if old_rank_match:
            old_rank = int(old_rank_match.group(1))
            old_to_new[old_rank] = new_rank

    print(f"编号映射: {len(old_to_new)} 个")

    # ── 4. 重建总表 ──
    # 表头 + 分隔行 + 排序后的数据行
    header_idx = None
    sep_idx = None
    for i in range(main_start, main_end):
        s = lines[i].strip()
        if s.startswith('|') and '排名' in s and '问题' in s:
            header_idx = i
        if header_idx is not None and i > header_idx and re.match(r'^\|[-:\s]+(\|[-:\s]+)*\|\s*$', s):
            sep_idx = i
            break

    print(f"表头: {header_idx}, 分隔行: {sep_idx}")

    # 构建新表格行
    new_table_lines = []
    new_table_lines.append(lines[header_idx])
    new_table_lines.append(lines[sep_idx])

    for new_rank, (idx, cells) in enumerate(sorted_rows, 1):
        # 更新排名编号
        old_cell = cells[0]
        # 提取旧编号，替换为新编号
        new_cell = re.sub(r'\d+', str(new_rank), old_cell, count=1)
        cells[0] = new_cell
        new_line = '| ' + ' | '.join(cells) + ' |\n'
        new_table_lines.append(new_line)

    # ── 5. 替换文件中的主表 ──
    first_data = table_indices[0]
    last_data = table_indices[-1]
    new_content_lines = lines[:first_data] + new_table_lines[2:] + lines[last_data + 1:]

    # ── 6. 更新文件中所有引用旧编号的地方 ──
    # 分榜引用格式: #1, #2, #3 等
    content = ''.join(new_content_lines)

    def update_refs(text):
        def replace(m):
            num = int(m.group(1))
            if num in old_to_new:
                return f'#{old_to_new[num]}'
            return m.group(0)
        return re.sub(r'#(\d+)', replace, text)

    content = update_refs(content)

    # ── 7. 处理分榜表格排序 ──
    # 找到每个分榜 ### 标题的位置
    lines2 = content.split('\n')

    # 找到所有 ### 标题
    section_indices = []
    for i, line in enumerate(lines2):
        m = re.match(r'^(###\s+\S.*)', line)
        if m:
            section_indices.append(i)

    print(f"找到 {len(section_indices)} 个章节标题")

    # 对每个分榜区域处理
    for si in range(len(section_indices)):
        start = section_indices[si]
        end = section_indices[si + 1] if si + 1 < len(section_indices) else len(lines2)

        section_text = '\n'.join(lines2[start:end])
        section_lines = lines2[start:end]

        # 检查是否包含分榜表格（表头含"排名 | 问题 | 频率"）
        has_subtable = False
        for line in section_lines:
            if re.search(r'\|\s*排名?\s*\|\s*问题', line):
                has_subtable = True
                break

        if not has_subtable:
            continue

        print(f"\n处理分榜: {lines2[start].strip()}")

        # 找到分榜表格行
        sub_rows = []
        for i, line in enumerate(section_lines):
            if is_table_row(line):
                cells = parse_row(line)
                if len(cells) >= 3:
                    # cells[0] = 排名, cells[1] = 问题, cells[2] = 频率
                    freq = cells[2] if len(cells) > 2 else ''
                    sub_rows.append((i, line, freq, cells))

        if not sub_rows:
            continue

        # 排序
        def sub_sort_key(item):
            _, _, freq, cells = item
            return (-freq_score(freq)[0], cells[1] if len(cells) > 1 else '')

        sorted_sub = sorted(sub_rows, key=sub_sort_key)

        # 替换表格行
        # 找到第一个和最后一个表格行的索引
        sub_indices = [r[0] for r in sub_rows]
        first_sub = min(sub_indices)
        last_sub = max(sub_indices)

        # 构建新行
        new_rows = []
        for r in sorted_sub:
            new_rows.append(r[1])

        # 替换
        lines2[start + first_sub:start + last_sub + 1] = new_rows

        print(f"  重排 {len(sub_rows)} 行")

    # ── 8. 写回 ──
    final_content = '\n'.join(lines2)
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"\n✅ 完成！{len(rows)} 条总榜 + 分榜重排")
    for old, new in sorted(old_to_new.items()):
        print(f"  #{old} → #{new}")

if __name__ == '__main__':
    main()
