# -*- coding: utf-8 -*-
"""
AI营养师 · 大健康落地实战分享  ——  全篇黑底版（精简重构）
风格：Modern Newspaper × 瑞士/包豪斯 · 纯黑底 + 白字 + 电光黄点缀 · 非对称布局 · 超大标题
前置：AI 已是既定事实 → 前半段只做「一句话立底 + 84% 数据 + 两个方向」
      核心：① AI 打通专业（营养师大脑可复制）② AI 打通创作（自媒体大脑）
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ---------- 调色板（黑底） ----------
BG    = RGBColor(0x11, 0x11, 0x11)   # 页面底 · 墨黑
SURF  = RGBColor(0x1B, 0x1B, 0x1B)   # 卡片面
LINE  = RGBColor(0x33, 0x33, 0x33)   # 分隔线 / 边框
T1    = RGBColor(0xFF, 0xFF, 0xFF)   # 主文字 · 白
T2    = RGBColor(0xA8, 0xA8, 0xA8)   # 次文字 · 灰
T3    = RGBColor(0x6E, 0x6E, 0x6E)   # 弱文字 · 深灰
YEL   = RGBColor(0xFF, 0xCC, 0x00)   # 电光黄
RED   = RGBColor(0xFF, 0x3B, 0x3B)   # 警报红

F_HEI = 'Hiragino Sans GB'   # 中文黑体
F_IMP = 'Impact'             # 拉丁超粗
F_HEL = 'Helvetica Neue'     # 拉丁细
F_SER = 'Songti SC'          # 中文宋体

W, H = 13.333, 7.5
N_TOTAL = 22

prs = Presentation()
prs.slide_width  = Inches(W)
prs.slide_height = Inches(H)


# ---------- 基础工具 ----------
def _cjk(run, font):
    rPr = run._r.get_or_add_rPr()
    for tag in ('a:ea', 'a:cs'):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {})
            rPr.append(el)
        el.set('typeface', font)


def style_run(r, text, size, color, bold, font, spc=None):
    r.text = text
    f = r.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = font
    _cjk(r, font)
    if spc is not None:
        r._r.get_or_add_rPr().set('spc', str(int(spc * 100)))


def new_slide(bg=BG):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    return s


def rect(s, l, t, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    shp = s.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    shp.text_frame.word_wrap = True
    return shp


def card(s, l, t, w, h, fill=SURF, border=LINE, accent=False, accent_w=0.13):
    shp = rect(s, l, t, w, h, fill=fill, line=border, lw=0.75)
    if accent:
        rect(s, l, t, accent_w, h, fill=YEL)
    return shp


def add_text(s, l, t, w, h, text, size=14, color=T1, bold=False, font=F_HEI,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=1.15, spc=None,
             wrap=True, rich=None):
    box = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    try:
        tf.vertical_anchor = anchor
    except Exception:
        pass

    lines = rich if rich is not None else [(text, size, color, bold, font)]
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = ls
        runs = item if isinstance(item, list) else [item]
        for rspec in runs:
            txt, sz, col, bd, fn = rspec[:5]
            r = p.add_run()
            style_run(r, txt, sz, col, bd, fn)
    return box


def shape_text(shp, text, size=12, color=T1, bold=False, font=F_HEI,
               align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE, ls=1.25,
               pad=(0.18, 0.18, 0.12, 0.12)):
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(pad[0]); tf.margin_right = Inches(pad[1])
    tf.margin_top = Inches(pad[2]);  tf.margin_bottom = Inches(pad[3])
    try:
        tf.vertical_anchor = anchor
    except Exception:
        pass
    for i, line in enumerate(text.split('\n')):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = ls
        r = p.add_run()
        style_run(r, line, size, color, bold, font)
    return shp


def crop_marks(s, color=T1, m=0.20, L=0.14, th=0.014):
    for (cx, cy, sx, sy) in [(m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)]:
        x = cx if sx > 0 else cx - L
        rect(s, x, cy - th / 2, L, th, fill=color)
        y = cy if sy > 0 else cy - L
        rect(s, cx - th / 2, y, th, L, fill=color)


def chrome(s, page, sec=''):
    if sec:
        add_text(s, 0.85, 0.44, 8.5, 0.28, sec, size=9, color=T3, font=F_HEI, spc=1.4)
    crop_marks(s)
    frac = page / N_TOTAL
    rect(s, 0, H - 0.055, W * frac, 0.055, fill=YEL)
    rect(s, W * frac, H - 0.055, W * (1 - frac), 0.055, fill=LINE)
    add_text(s, 11.4, H - 0.44, 1.1, 0.24, "%02d / %02d" % (page, N_TOTAL),
             size=9, color=T2, font=F_HEL, align=PP_ALIGN.RIGHT)


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


# ============================================================
# S1 封面
# ============================================================
s = new_slide()
add_text(s, 0.9, 0.55, 6, 0.3, "张医生 · AI 营养师", size=11, color=T1, spc=1.8)
add_text(s, 8.0, 0.55, 4.4, 0.3, "AI · 大健康 · 落地实战", size=11, color=T2,
         align=PP_ALIGN.RIGHT, spc=1.8)

add_text(s, 0.85, 2.05, 9.5, 3.2, "",
         rich=[[("推", 175, T1, True, F_HEI), ("平", 175, YEL, True, F_HEI)]], ls=1.0)

rect(s, 0.9, 5.22, 2.6, 0.045, fill=YEL)
add_text(s, 0.9, 5.48, 7.6, 0.6, "AI 把信息推平之后，普通人的最后一次机遇",
         size=21, color=YEL, font=F_SER)
add_text(s, 8.35, 5.44, 4.15, 1.2,
         "授课 + 实操｜现场搭建\n「营养师大脑」与「自媒体大脑」",
         size=10.5, color=T2, ls=1.5)

add_text(s, 0.9, 6.50, 8, 0.3, "2026.09 · 内部实战分享", size=10, color=T3, font=F_HEL, spc=1.2)
crop_marks(s)
notes(s, "开场一句话：AI 不用我论证了，今天只讲两件事——它怎么打通你的专业，怎么打通你的创作。")

# ============================================================
# S2 目录
# ============================================================
s = new_slide()
chrome(s, 2, "CONTENTS · 今晚讲什么")
add_text(s, 0.9, 1.35, 11, 1.0, "两个部分", size=60, color=T1, bold=True)

rect(s, 0.9, 2.78, 11.55, 0.02, fill=LINE)
add_text(s, 0.9, 2.95, 2.0, 1.5, "01", size=76, color=YEL, bold=True, font=F_IMP)
add_text(s, 2.75, 3.18, 8.5, 0.6, "授课", size=32, color=T1, bold=True)
add_text(s, 2.80, 3.72, 9.5, 0.4, "商业的本质 · 84% 的时代风口 · 两个方向", size=14, color=T2)

rect(s, 0.9, 4.58, 11.55, 0.02, fill=LINE)
add_text(s, 0.9, 4.75, 2.0, 1.5, "02", size=76, color=YEL, bold=True, font=F_IMP)
add_text(s, 2.75, 4.98, 8.5, 0.6, "实操", size=32, color=T1, bold=True)
add_text(s, 2.80, 5.52, 9.5, 0.4, "现场演示：搭建「营养师大脑」与「自媒体大脑」", size=14, color=T2)
rect(s, 0.9, 6.38, 11.55, 0.02, fill=LINE)
notes(s, "上半场很短：立一个底、给一个数据、指两个方向。下半场直接动手。")

# ============================================================
# S3 章节页 01
# ============================================================
s = new_slide()
chrome(s, 3, "PART 01 / 02")
add_text(s, 0.85, 1.05, 3.0, 1.6, "01", size=104, color=YEL, bold=True, font=F_IMP)
add_text(s, 0.85, 2.70, 8.0, 2.2, "授课", size=132, color=T1, bold=True, ls=1.0)
rect(s, 0.9, 5.30, 2.4, 0.045, fill=YEL)
add_text(s, 0.9, 5.52, 10, 0.5, "一句话立底 · 一个数据 · 两个方向", size=18, color=T2)
notes(s, "第一部分只讲三件事，十分钟讲完。")

# ============================================================
# S4 商业的本质（一句话立底）
# ============================================================
s = new_slide()
chrome(s, 4, "01 · 授课 — 一句话立底")
add_text(s, 0.9, 1.50, 11.5, 2.6,
         "金钱的本质，\n是信息在创造价值", size=60, color=T1, bold=True, ls=1.18)
rect(s, 0.9, 4.26, 4.6, 0.11, fill=YEL)
add_text(s, 0.9, 4.54, 6, 0.4, "——《人类简史》", size=15, color=T2, font=F_SER)
add_text(s, 0.9, 5.30, 11.4, 1.4,
         "所有生意，本质上都在处理同一件事：信息。\n信息差，就是财富差。",
         size=19, color=T1, ls=1.5)
add_text(s, 0.9, 6.55, 11.4, 0.4,
         "过去一切生意，都建立在「我知道的，你不知道」之上。这一层，AI 把它推平了。",
         size=13, color=T3)
notes(s, "只立一个底：《人类简史》讲得很清楚，金钱是一套共同相信的信息。所以商业的底层，从头到尾都是信息在创造价值。")

# ============================================================
# S5 AI 把信息推平了（一句话带过）
# ============================================================
s = new_slide()
chrome(s, 5, "01 · 授课 — 一句话带过")
add_text(s, 0.9, 1.55, 11.5, 1.6, "",
         rich=[[("AI，把信息", 60, T1, True, F_HEI),
                ("推平", 60, YEL, True, F_HEI),
                ("了", 60, T1, True, F_HEI)]], ls=1.1)
rect(s, 0.9, 3.28, 6.6, 0.11, fill=YEL)
add_text(s, 0.9, 3.66, 11.2, 1.6,
         "任何人、任何行业，一键就能拿到最核心的信息与技术。\n信息差正在消失 —— 靠「我知道你不知道」赚钱的时代，结束了。",
         size=18, color=T2, ls=1.5)
add_text(s, 0.9, 5.70, 11.4, 0.5,
         "这件事不用再论证。AI 已经是既定事实。", size=22, color=T1, bold=True)
notes(s, "这一页只用一句话带过：AI 已经把信息门槛推平了。不用再论证 AI 行不行，它已经是既定事实。")

# ============================================================
# S6 · 84%（数据页）
# ============================================================
s = new_slide()
chrome(s, 6, "01 · 授课 — 但是")
add_text(s, 0.9, 0.88, 6, 0.5, "但是 ——", size=18, color=T3)
add_text(s, 0.72, 1.68, 8.5, 4.2, "84%", size=250, color=YEL, bold=True, font=F_IMP, ls=0.9)
cd = card(s, 7.55, 3.85, 4.95, 2.10, accent=True)
shape_text(cd, "全球约 68 亿人，\n从未用过 AI。\n真正付费使用的，只有 0.3%。",
           size=20, color=T1, bold=True, ls=1.35, anchor=MSO_ANCHOR.MIDDLE,
           pad=(0.55, 0.35, 0.28, 0.28))
add_text(s, 0.9, 6.62, 11.5, 0.4,
         "数据：2026 年全球 AI 使用分布统计（各机构估算区间 72%–84%，取最广泛引用的 84%）· Microsoft Q1 2026：仅 17.8% 劳动年龄人口用过生成式 AI",
         size=8.5, color=T3)
notes(s, "这是全场最重要的一个数字。全球 84% 的人从没用过 AI，真正付费的只有 0.3%。"
         "也就是说，AI 推平了门槛，但绝大多数人还没进门——这就是这一波的信息差。")

# ============================================================
# S7 那么，普通人怎么布局？
# ============================================================
s = new_slide()
chrome(s, 7, "01 · 授课 — 那么")
add_text(s, 0.9, 1.40, 11.5, 0.7, "那么，普通人怎么布局？", size=56, color=T1, bold=True)
rect(s, 0.9, 2.45, 5.4, 0.11, fill=YEL)

dirs = [("方向一", "专业", "让 AI 打通你的专业", "把行业最核心的信息，装进 AI"),
        ("方向二", "流量", "让 AI 打通你的创作", "把有价值的信息，交付给人")]
for i, (tag, key, title, desc) in enumerate(dirs):
    y = 3.05 + i * 1.72
    card(s, 0.9, y, 11.55, 1.50, accent=True)
    add_text(s, 1.30, y + 0.28, 2.0, 0.35, tag, size=12, color=T3, spc=1.2)
    add_text(s, 3.10, y + 0.22, 2.6, 0.7, key, size=32, color=YEL, bold=True)
    add_text(s, 5.70, y + 0.26, 6.4, 0.6, title, size=22, color=T1, bold=True)
    add_text(s, 5.72, y + 0.86, 6.4, 0.4, desc, size=13, color=T2)
notes(s, "那普通人到底怎么布局？就两个方向：一是让 AI 打通你的专业，二是让 AI 打通你的创作。"
         "一个解决专业能力，一个解决触达能力。")

# ============================================================
# S8 方向一 · 专业
# ============================================================
s = new_slide()
chrome(s, 8, "01 · 授课 — 方向一 · 专业")
add_text(s, 0.9, 1.15, 11.5, 0.6, "方向一 · 专业", size=18, color=YEL, bold=True)
add_text(s, 0.9, 1.75, 11.5, 1.2, "AI 打通专业", size=64, color=T1, bold=True)
rect(s, 0.9, 3.10, 5.0, 0.11, fill=YEL)
add_text(s, 0.9, 3.52, 11.3, 1.6,
         "把最权威的专业信息装进 AI ——\n你的专业能力，不再只长在你一个人身上。",
         size=19, color=T2, ls=1.5)

steps = [("01", "喂进专业信息", "权威书籍 · 行业资料"), ("02", "给它方案样板", "你的标准 = 它的标准"), ("03", "营养师大脑", "可复制 · 可交付")]
for i, (num, t, d) in enumerate(steps):
    x = 0.9 + i * 3.95
    last = (i == 2)
    card(s, x, 5.10, 3.45, 1.35, fill=(YEL if last else SURF), border=(None if last else LINE))
    add_text(s, x + 0.28, 5.28, 2, 0.3, num, size=12, color=(BG if last else T3), bold=True, font=F_IMP)
    add_text(s, x + 0.28, 5.60, 3.0, 0.4, t, size=18, color=(BG if last else T1), bold=True)
    add_text(s, x + 0.28, 6.02, 3.0, 0.3, d, size=11, color=(BG if last else T2))
    if i < 2:
        add_text(s, x + 3.45, 5.62, 0.55, 0.4, "→", size=20, color=YEL, bold=True,
                 align=PP_ALIGN.CENTER, wrap=False)
notes(s, "方向一，专业。把权威信息喂进 AI，给它一个方案样板，你就得到一个可复制的营养师大脑。"
         "过去专业只长在你一个人身上，现在它能被复制、被交付。")

# ============================================================
# S9 方向二 · 流量
# ============================================================
s = new_slide()
chrome(s, 9, "01 · 授课 — 方向二 · 流量")
add_text(s, 0.9, 1.15, 11.5, 0.6, "方向二 · 流量", size=18, color=YEL, bold=True)
add_text(s, 0.9, 1.75, 11.5, 1.2, "AI 打通创作", size=64, color=T1, bold=True)
rect(s, 0.9, 3.10, 5.0, 0.11, fill=YEL)
add_text(s, 0.9, 3.52, 11.3, 1.6,
         "信息不等于商业 —— 必须交付出去，才产生价值。\n而自媒体，就是那个交付的出口。",
         size=19, color=T2, ls=1.5)

steps = [("01", "给创作规则", "选题 · 结构 · 爆款逻辑"), ("02", "给一个选题", "一句话就够"), ("03", "自媒体大脑", "脚本 · 成片 · 触达")]
for i, (num, t, d) in enumerate(steps):
    x = 0.9 + i * 3.95
    last = (i == 2)
    card(s, x, 5.10, 3.45, 1.35, fill=(YEL if last else SURF), border=(None if last else LINE))
    add_text(s, x + 0.28, 5.28, 2, 0.3, num, size=12, color=(BG if last else T3), bold=True, font=F_IMP)
    add_text(s, x + 0.28, 5.60, 3.0, 0.4, t, size=18, color=(BG if last else T1), bold=True)
    add_text(s, x + 0.28, 6.02, 3.0, 0.3, d, size=11, color=(BG if last else T2))
    if i < 2:
        add_text(s, x + 3.45, 5.62, 0.55, 0.4, "→", size=20, color=YEL, bold=True,
                 align=PP_ALIGN.CENTER, wrap=False)
notes(s, "方向二，流量。信息不交付出去就没有价值。给 AI 一套创作规则，再给一个选题，"
         "它就能出脚本、出成片，把有价值的信息送到人面前。")

# ============================================================
# S10 落在大健康
# ============================================================
s = new_slide()
chrome(s, 10, "01 · 授课 — 落地行业")
add_text(s, 0.9, 1.30, 11.5, 1.6, "而这一切，落在大健康", size=62, color=T1, bold=True)
rect(s, 0.9, 3.05, 5.4, 0.11, fill=YEL)
add_text(s, 0.9, 3.50, 11.3, 1.6,
         "人群最广、需求最刚、复购最强。\n慢病解决方案与营养管理 —— 周期长、信任重、极度依赖专业，正是 AI 最能放大的地方。",
         size=19, color=T2, ls=1.5)
add_text(s, 0.9, 5.85, 11.2, 0.4,
         "以上为健康科普分享，不构成诊疗建议，个体情况请咨询专业医师。",
         size=9.5, color=T3)
notes(s, "为什么落在大健康？人群最广、需求最刚、复购最强。而慢病和营养，周期长、信任重、"
         "极度依赖专业——这正是 AI 最能放大的地方。")

# ============================================================
# S11 落地模型：两个大脑
# ============================================================
s = new_slide()
chrome(s, 11, "01 · 授课 — 落地模型")
add_text(s, 0.9, 1.20, 11.5, 0.9, "AI 营养师 = 两个大脑", size=54, color=T1, bold=True)

cards = [
    ("01", "营养师大脑", "行业里最有价值的专业信息", "慢病 · 营养 · 方案"),
    ("02", "自媒体大脑", "内容创作与流量的信息", "选题 · 脚本 · 爆款"),
]
for i, (num, title, desc, tag) in enumerate(cards):
    x = 0.9 + i * 6.35
    card(s, x, 2.55, 5.65, 3.35)
    rect(s, x, 2.55, 5.65, 0.10, fill=YEL)
    add_text(s, x + 0.35, 2.90, 2, 0.5, num, size=22, color=YEL, bold=True, font=F_IMP)
    add_text(s, x + 0.35, 3.35, 5.0, 0.8, title, size=32, color=T1, bold=True)
    add_text(s, x + 0.35, 4.28, 5.0, 0.7, desc, size=15, color=T2)
    add_text(s, x + 0.35, 5.20, 5.0, 0.4, tag, size=12, color=T3, font=F_SER)

add_text(s, 6.30, 3.95, 1.0, 0.6, "+", size=40, color=YEL, bold=True,
         align=PP_ALIGN.CENTER, wrap=False)
notes(s, "落地就靠两个大脑：营养师大脑解决专业，自媒体大脑解决流量。这两个大脑，今晚我都会当场搭给你看。")

# ============================================================
# S12 成为专家，找到人群
# ============================================================
s = new_slide()
chrome(s, 12, "01 · 授课 — 闭环")
add_text(s, 0.9, 1.35, 11.5, 1.0, "成为专家，找到人群", size=58, color=T1, bold=True)

steps = [("用 AI 成为\n行业专家", False), ("用 AI 触达\n更多人群", False),
         ("完成交付\n形成闭环", True), ("获得\n商业回报", True)]
for i, (txt, hot) in enumerate(steps):
    x = 0.9 + i * 3.02
    card(s, x, 2.85, 2.72, 2.35, fill=(YEL if hot else SURF),
         border=(None if hot else LINE))
    add_text(s, x + 0.25, 3.35, 2.3, 1.4, txt, size=19,
             color=(BG if hot else T1), bold=True, ls=1.35)
    if i < 3:
        add_text(s, x + 2.74, 3.75, 0.30, 0.5, "→", size=22, color=YEL, bold=True,
                 align=PP_ALIGN.CENTER, wrap=False)

add_text(s, 0.9, 5.70, 11.5, 0.8,
         "商业的本质，就这样被你完整跑通了一遍。",
         size=18, color=T2, font=F_SER)
notes(s, "专家 + 人群 + 交付 = 闭环。这不是理论，这是可以一步一步做出来的路径。")

# ============================================================
# S13 一人公司
# ============================================================
s = new_slide()
chrome(s, 13, "01 · 授课 — 一人公司")
add_text(s, 0.9, 1.02, 11.5, 1.5, "一人公司", size=78, color=T1, bold=True)
rect(s, 0.9, 2.62, 5.0, 0.11, fill=YEL)
add_text(s, 0.9, 3.02, 11.3, 1.2,
         "借助 AI，一个人就能完成一整家公司的工作 ——\n从信息获取、自媒体创作，到文案、课程、剪辑、交付与客服，全链路一个人跑完。",
         size=17, color=T2, ls=1.5)

jobs = ["信息获取", "文案编辑", "课程创作", "拍摄剪辑", "交付服务", "客户服务"]
CW, GAP = 1.7425, 0.22
for i, j in enumerate(jobs):
    x = 0.9 + i * (CW + GAP)
    card(s, x, 4.20, CW, 1.30)
    add_text(s, x + 0.20, 4.42, CW - 0.34, 0.3, "%02d" % (i + 1), size=12,
             color=YEL, bold=True, font=F_IMP)
    add_text(s, x + 0.20, 4.88, CW - 0.36, 0.5, j, size=16, color=T1, bold=True)

band = rect(s, 0.9, 5.92, 11.55, 0.72, fill=YEL)
shape_text(band, "过去，这是一支团队。现在，是一个人。", size=17, color=BG, bold=True,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "这一页是重点：AI 不是帮你省一点时间，是让你一个人具备一整条产线的能力。"
         "信息获取、文案、课程、剪辑、交付、客服，过去每一个都要一个人，现在一个人全包。")

# ============================================================
# S14 一人公司 · 成本对比
# ============================================================
s = new_slide()
chrome(s, 14, "01 · 授课 — 一人公司 · 成本")
add_text(s, 0.9, 0.98, 11.5, 0.9, "一个人，抵一个团队", size=44, color=T1, bold=True)
add_text(s, 0.9, 1.74, 11.5, 0.4, "过去这些活儿，要请 6 个人来做。", size=15, color=T2)

JOBS = [("文案编辑", 6000), ("内容运营", 7000), ("拍摄", 7000),
        ("剪辑", 7000), ("课程教研", 10000), ("客户服务", 5000)]
TOT = sum(v for _, v in JOBS)
BARW = 10.50
TONES = [0x24, 0x30, 0x3C, 0x48, 0x54, 0x60]

add_text(s, 0.9, 2.34, 9.0, 0.3, "过去 · 6 个岗位 · 每月", size=11, color=T3, spc=1.2)
x = 0.9
for i, (name, val) in enumerate(JOBS):
    wseg = BARW * val / TOT
    rect(s, x, 2.62, wseg, 0.95, fill=RGBColor(TONES[i], TONES[i], TONES[i]), line=BG, lw=1.0)
    add_text(s, x + 0.13, 2.78, wseg - 0.22, 0.3, name, size=10.5, color=T1, bold=True)
    add_text(s, x + 0.13, 3.08, wseg - 0.22, 0.35, "¥%s" % format(val, ","),
             size=12.5, color=YEL, bold=True, font=F_HEL)
    x += wseg

add_text(s, 0.9, 3.70, 6.0, 0.4, "合计 ¥%s / 月" % format(TOT, ","), size=19, color=T1, bold=True)
add_text(s, 6.6, 3.76, 5.9, 0.3, "参考市场月薪测算 · 按你当地行情调整",
         size=9.5, color=T3, align=PP_ALIGN.RIGHT)

add_text(s, 0.9, 4.32, 9.0, 0.3, "现在 · 一个人 + AI · 每月", size=11, color=T3, spc=1.2)
rect(s, 0.9, 4.58, 0.34, 0.95, fill=YEL)
add_text(s, 1.48, 4.62, 4.5, 0.5, "¥350 / 月", size=22, color=YEL, bold=True)
add_text(s, 1.48, 5.16, 8.5, 0.35,
         "大模型会员 ¥200 ＋ AI 剪辑 ¥100 ＋ 素材工具 ¥50", size=10.5, color=T2)

add_text(s, 0.9, 5.92, 7.5, 1.0, "成本 ≈ 1%", size=54, color=YEL, bold=True)
add_text(s, 7.6, 6.38, 4.9, 0.4, "同样的活儿，一个人 ＋ AI 跑完。",
         size=14, color=T2, align=PP_ALIGN.RIGHT)
notes(s, "关键对比：过去 6 个岗位、一个月四万二；现在一个人加 AI，一个月三百五。"
         "数字是按市场行情估的，讲的时候可以按当地实际工资替换。这里讲的不是省钱，是产能。")

# ============================================================
# S15 小结
# ============================================================
s = new_slide()
chrome(s, 15, "01 · 授课 — 小结")
add_text(s, 0.9, 1.55, 11.5, 1.5, "两个方向，一个闭环", size=72, color=T1, bold=True)
rect(s, 0.9, 3.35, 5.4, 0.12, fill=YEL)
add_text(s, 0.9, 3.80, 11.4, 1.8,
         "AI 打通专业 ＋ AI 打通创作\n= 一个人，跑完整个商业闭环",
         size=24, color=YEL, ls=1.5, font=F_SER)
notes(s, "第一部分收口：专业和流量两个方向打通，剩下的就是一个人跑完闭环。")

# ============================================================
# S16 章节页 02
# ============================================================
s = new_slide()
chrome(s, 16, "PART 02 / 02")
add_text(s, 0.85, 1.05, 3.0, 1.6, "02", size=104, color=YEL, bold=True, font=F_IMP)
add_text(s, 0.85, 2.70, 8.0, 2.2, "实操", size=132, color=T1, bold=True, ls=1.0)
rect(s, 0.9, 5.30, 2.4, 0.045, fill=YEL)
add_text(s, 0.9, 5.52, 10.5, 0.5, "看我的电脑 · 现场搭两个大脑", size=18, color=T2)
notes(s, "下半场不讲道理，只动手。我先把电脑打开给你看，然后一步一步教你搭。")

# ============================================================
# S17 先看我的电脑
# ============================================================
s = new_slide()
chrome(s, 17, "02 · 实操 — 先看结果")
add_text(s, 0.9, 1.20, 11.5, 1.0, "先看我的电脑", size=58, color=T1, bold=True)

two = [("A", "知识沉淀大脑", "这些年积累的营养 · 慢病 · 方案素材，全部结构化沉淀"),
       ("B", "自媒体大脑", "选题库 · 爆款库 · 脚本规则，全部沉淀成可调用的资产")]
for i, (k, title, desc) in enumerate(two):
    x = 0.9 + i * 6.35
    card(s, x, 2.70, 5.65, 2.05, accent=True)
    add_text(s, x + 0.48, 3.05, 2, 0.5, k, size=26, color=YEL, bold=True, font=F_IMP)
    add_text(s, x + 1.10, 3.08, 4.4, 0.6, title, size=26, color=T1, bold=True)
    add_text(s, x + 1.10, 3.75, 4.4, 0.9, desc, size=13, color=T2, ls=1.45)

band = rect(s, 0.9, 5.25, 11.55, 1.05, fill=YEL)
shape_text(band, "  这两个大脑不是天生的，也不是买的 —— 是攒出来的。\n  接下来，我教你怎么从零搭起来。",
           size=16, color=BG, bold=True, anchor=MSO_ANCHOR.MIDDLE)
notes(s, "先给你们看成品。这两个大脑，一个是专业知识，一个是自媒体能力。看完了，我们开始搭。")

# ============================================================
# S18 实操一
# ============================================================
s = new_slide()
chrome(s, 18, "02 · 实操 一 — 营养师大脑")
add_text(s, 0.9, 1.15, 11.5, 0.7, "实操一", size=20, color=YEL, bold=True)
add_text(s, 0.9, 1.70, 11.5, 1.0, "用豆包，搭一个营养师大脑", size=46, color=T1, bold=True)
rect(s, 0.9, 2.95, 5.2, 0.11, fill=YEL)

add_text(s, 0.9, 3.35, 11.5, 0.5, "两步，就两步：", size=17, color=T2)
for i, (num, t, d) in enumerate([
        ("第一步", "先把专业书「喂」进去", "让大脑拥有这个行业最核心的信息"),
        ("第二步", "再给它一个方案样板", "让它照着样板，直接出解决方案")]):
    x = 0.9 + i * 6.35
    card(s, x, 4.05, 5.65, 1.95)
    add_text(s, x + 0.35, 4.32, 3, 0.4, num, size=14, color=RED, bold=True)
    add_text(s, x + 0.35, 4.72, 5.0, 0.6, t, size=24, color=T1, bold=True)
    add_text(s, x + 0.35, 5.32, 5.0, 0.5, d, size=13, color=T2)
notes(s, "营养师大脑的搭建只有两步：喂书，给样板。下面我把提示词一条一条给你。")

# ============================================================
# S19 提示词一
# ============================================================
s = new_slide()
chrome(s, 19, "02 · 实操 一 — 提示词 ①")
add_text(s, 0.9, 1.05, 11.5, 0.9, "提示词 ①：把书喂进去", size=42, color=T1, bold=True)

box = card(s, 0.9, 2.20, 7.6, 4.25, accent=True)
shape_text(box,
           "请你作为一位资深临床营养师。\n\n"
           "以下内容是你必须掌握的专业知识基础：\n"
           "·《科学营养圣经》\n"
           "·《中国营养学会 · 膳食营养素参考摄入量》\n"
           "·《临床药学》\n"
           "·（以及你手上所有权威营养学资料）\n\n"
           "请全部学习并记住，作为你后续所有方案的依据。",
           size=14, color=T1, ls=1.55, anchor=MSO_ANCHOR.TOP, pad=(0.45, 0.35, 0.35, 0.3))

add_text(s, 8.85, 2.25, 3.7, 0.4, "为什么要喂书？", size=15, color=T1, bold=True)
rect(s, 8.85, 2.72, 1.6, 0.06, fill=YEL)
add_text(s, 8.85, 3.00, 3.7, 3.3,
         "· 让回答有据可依，不瞎编\n\n"
         "· 统一口径，避免前后矛盾\n\n"
         "· 权威来源 = 专业感与信任感\n\n"
         "· 一次喂好，长期复用",
         size=13.5, color=T2, ls=1.5)
notes(s, "第一条提示词，是把书喂进去。注意：书单要写具体，越权威越好。这一步决定了这个大脑的天花板。")

# ============================================================
# S20 提示词二
# ============================================================
s = new_slide()
chrome(s, 20, "02 · 实操 一 — 提示词 ②")
add_text(s, 0.9, 1.05, 11.5, 0.9, "提示词 ②：给它一个方案样板", size=42, color=T1, bold=True)

box = card(s, 0.9, 2.20, 7.6, 4.25, accent=True)
shape_text(box,
           "这是我们的标准方案样板：\n"
           "〔此处粘贴一份你写好的完整方案〕\n\n"
           "从现在起，请严格按照这个样板的\n"
           "结构、语气、颗粒度来输出。\n\n"
           "接下来我会给你客户的疾病与症状，\n"
           "请你直接输出一份完整、可交付的\n"
           "调理解决方案。",
           size=14, color=T1, ls=1.55, anchor=MSO_ANCHOR.TOP, pad=(0.45, 0.35, 0.35, 0.3))

add_text(s, 8.85, 2.25, 3.7, 0.4, "工作方式", size=15, color=T1, bold=True)
rect(s, 8.85, 2.72, 1.6, 0.06, fill=YEL)
flow = ["疾病 · 症状", "按样板生成", "完整解决方案"]
for i, f in enumerate(flow):
    y = 3.05 + i * 0.92
    last = (i == 2)
    shape_text(card(s, 8.85, y, 3.7, 0.66, fill=(YEL if last else SURF),
                    border=(None if last else LINE)),
               f, size=15, color=(BG if last else T1), bold=True, align=PP_ALIGN.CENTER)
    if i < 2:
        add_text(s, 10.6, y + 0.68, 0.4, 0.24, "↓", size=14, color=YEL, bold=True,
                 align=PP_ALIGN.CENTER, wrap=False)
notes(s, "第二条提示词，是给它一个样板。样板就是标准，你给多好的样板，它就出多好的方案。")

# ============================================================
# S21 实操二
# ============================================================
s = new_slide()
chrome(s, 21, "02 · 实操 二 — 自媒体大脑")
add_text(s, 0.9, 1.15, 11.5, 0.7, "实操二", size=20, color=YEL, bold=True)
add_text(s, 0.9, 1.70, 11.5, 1.0, "一个提示词，直接出爆款脚本", size=46, color=T1, bold=True)
rect(s, 0.9, 2.95, 5.2, 0.11, fill=YEL)

box = card(s, 0.9, 3.35, 7.6, 3.10, accent=True)
shape_text(box,
           "你是我的短视频创作助手。\n\n"
           "这是我的脚本创作规则：\n"
           "〔粘贴你的创作脚本提示词〕\n\n"
           "现在我给你一个选题，\n"
           "请直接输出一条完整、可拍的口播脚本。",
           size=14, color=T1, ls=1.55, anchor=MSO_ANCHOR.TOP, pad=(0.45, 0.35, 0.35, 0.3))

add_text(s, 8.85, 3.40, 3.7, 0.4, "拿到就能拍", size=15, color=T1, bold=True)
rect(s, 8.85, 3.87, 1.6, 0.06, fill=YEL)
for i, f in enumerate(["给一个选题", "生成爆款脚本", "直接开拍"]):
    y = 4.20 + i * 0.62
    last = (i == 2)
    shape_text(card(s, 8.85, y, 3.7, 0.48, fill=(YEL if last else SURF),
                    border=(None if last else LINE)),
               f, size=14, color=(BG if last else T1), bold=True, align=PP_ALIGN.CENTER)
notes(s, "自媒体大脑更简单：一条提示词加一个选题，脚本直接出来。你只需要判断好不好，然后去拍。")

# ============================================================
# S22 结尾
# ============================================================
s = new_slide()
chrome(s, 22, "THE END · 现在开始")
add_text(s, 0.9, 1.40, 11.5, 2.4, "抓住这一波", size=104, color=T1, bold=True, ls=1.05)
rect(s, 0.9, 4.10, 5.0, 0.12, fill=YEL)
add_text(s, 0.9, 4.55, 11.4, 1.8,
         "AI 风口 × 大健康\n助力普通人，创造人生的机遇。",
         size=26, color=YEL, ls=1.5, font=F_SER)
add_text(s, 0.9, 6.35, 8, 0.4, "张医生 · AI 营养师｜2026.09", size=11, color=T3, font=F_HEL, spc=1.2)
notes(s, "收尾：84% 的人还没进来。你现在动手，就是那 16%。")

# ---------- 保存 ----------
out_dir = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(out_dir, 'AI营养师·大健康落地实战.pptx')
prs.save(out)
print('SAVED:', out)
print('SLIDES:', len(prs.slides))
