#!/usr/bin/env node
'use strict';
/**
 * sync-nav.js — 自动维护《视频号脚本风格系统.md》顶部 TOKNAV 行号导航块
 *
 * 触发：PostToolUse hook（matcher: Write|Edit）自动运行；
 *       也可手动：node .claude/scripts/sync-nav.js
 *
 * 设计要点：
 *   - 幂等：重复运行结果不变；失败静默退出（不抛错、不改动）
 *   - 锚点按标题层级精确匹配（level 精确），H2 主章节优先，避免被 H3 交叉引用抢占
 *   - 导航块行数恒定（同一批锚点 → 同一批行）→ 单轮收敛，替换不产生位移
 *   - 文件不存在 / 非目标文件时直接退出
 */
const fs = require('fs');
const path = require('path');

const FILE = '/Users/mac/Documents/zfc最强大脑/B自媒体大脑/01-视频号创作/创作脚本规则/视频号脚本风格系统.md';

const ANCHORS = [
  { id: 'verified', level: 3, needle: '已验证爆款公式' },
  { id: 'flow',     level: 1, needle: '写稿流程·八步' },
  { id: 'topic',    level: 2, needle: '〇、创作本质' },
  { id: 'idea',     level: 2, needle: '一、核心理念' },
  { id: 'pillar',   level: 2, needle: '二、三条风格支柱' },
  { id: 'rules',    level: 2, needle: '三、写作铁律' },
  { id: 'emotion',  level: 2, needle: '四、情绪曲线' },
  { id: 'opening',  level: 2, needle: '五、开头钩子公式库' },
  { id: 'closing',  level: 2, needle: '六、结尾钩子公式库' },
  { id: 'type',     level: 2, needle: '七、各脚本类型' },
  { id: 'check',    level: 2, needle: '八、写稿自检清单' },
  { id: 'refcase',  level: 2, needle: '九、参考：升级案例对比' },
  { id: 'refbench', level: 2, needle: '十、参考对标' },
  { id: 'traffic',  level: 2, needle: '十一、流量思维' },
  { id: 'realfeel', level: 2, needle: '十二、真实感写作法' },
  { id: 'links',    level: 2, needle: '十三、关联文件' },
];

const START = '<!--TOKNAV:start-->';
const END = '<!--TOKNAV:end-->';

function headingPositions(lines) {
  const pos = {};
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(#{1,6})\s+(.*?)\s*$/);
    if (!m) continue;
    const level = m[1].length;
    const text = m[2];
    for (const a of ANCHORS) {
      if (pos[a.id] === undefined && level === a.level && text.includes(a.needle)) {
        pos[a.id] = i + 1; // 1-based
      }
    }
  }
  return pos;
}

function buildBlock(pos, totalLines, kb) {
  const L = (id) => (pos[id] !== undefined ? String(pos[id]) : '?');
  return [
    START,
    `> ⚠️ **本文件 ≈${kb} KB / ${totalLines} 行 · 勿通读全文** —— 按行号跳读所需小节，省 90% tokens。`,
    `> 🎯 **写稿必读**：已验证爆款公式 → 行${L('verified')} ｜ 写稿八步 → 行${L('flow')} ｜ 写作铁律17条 → 行${L('rules')} ｜ 写稿自检 → 行${L('check')}`,
    `> 🔎 **卡哪查哪**：选题对位 → 〇章 行${L('topic')} ｜ 语气立场 → 一理念 行${L('idea')} ｜ 风格支柱 → 二章 行${L('pillar')} ｜ 情绪节奏 → 四章 行${L('emotion')} ｜ 开头3秒 → 五章 行${L('opening')} ｜ 结尾四拍 → 六章 行${L('closing')} ｜ 类型侧重 → 七章 行${L('type')} ｜ 流量完播 → 十一章 行${L('traffic')} ｜ 真实感口吻 → 十二章 行${L('realfeel')}`,
    `> ⏭️ **参考·默认跳过**：九章案例对比 行${L('refcase')} ｜ 十章对标 行${L('refbench')} ｜ 十三章关联 行${L('links')}`,
    `> 📌 Obsidian 直达：搜小节名如“五、开头钩子公式库”；Claude Code 用 Read(offset=行号-1)。`,
    END,
  ];
}

function isTargetFile(fp) {
  if (!fp) return false;
  const abs = path.resolve(fp);
  return abs === FILE;
}

function run(stdinJson) {
  // 若是 hook 调用且被编辑的不是目标文件 → 静默退出
  if (stdinJson && stdinJson.tool_input && !isTargetFile(stdinJson.tool_input.file_path)) {
    return;
  }
  if (!fs.existsSync(FILE)) return;
  let text;
  try { text = fs.readFileSync(FILE, 'utf8'); } catch (e) { return; }
  const lines = text.split('\n');
  const pos = headingPositions(lines);
  const totalLines = lines.length;

  try {
    if (!text.includes(START)) {
      // —— 首次插入：插到「已验证爆款公式」H3 之前 ——
      const idx = lines.findIndex((l) => {
        const m = l.match(/^#{3}\s+(.*)$/);
        return m && m[1].includes('已验证爆款公式');
      });
      const insertAt = idx < 0 ? 0 : idx;
      const draft = buildBlock(pos, totalLines, 0);
      const H = draft.length + 1; // 块 + 尾部空行
      const shifted = {};
      for (const a of ANCHORS) {
        shifted[a.id] =
          pos[a.id] !== undefined && pos[a.id] > insertAt ? pos[a.id] + H : pos[a.id];
      }
      const newTotal = totalLines + H;
      const fullText = lines.join('\n') + '\n' + draft.join('\n') + '\n';
      const kb = Math.max(1, Math.round(Buffer.byteLength(fullText, 'utf8') / 1024));
      const block = buildBlock(shifted, newTotal, kb);
      lines.splice(insertAt, 0, ...block, '');
      fs.writeFileSync(FILE, lines.join('\n'));
      return;
    }

    // —— 已存在：就地更新（保持行数不变 → 不产生位移）——
    const sIdx = lines.findIndex((l) => l.trim() === START);
    const eIdx = lines.findIndex((l) => l.trim() === END);
    if (sIdx < 0 || eIdx <= sIdx) return;
    const kb = Math.max(1, Math.round(Buffer.byteLength(text, 'utf8') / 1024));
    const block = buildBlock(pos, totalLines, kb);
    const inner = block.slice(1, -1);
    lines.splice(sIdx + 1, eIdx - sIdx - 1, ...inner);
    fs.writeFileSync(FILE, lines.join('\n'));
  } catch (e) {
    // 失败静默
  }
}

// —— 入口：hook 从 stdin 收 JSON；手动运行则无输入 ——
let raw = '';
try {
  raw = fs.readFileSync(0, 'utf8');
} catch (e) {
  raw = '';
}
let stdinJson = null;
if (raw.trim()) {
  try { stdinJson = JSON.parse(raw); } catch (e) { stdinJson = null; }
}
run(stdinJson);
