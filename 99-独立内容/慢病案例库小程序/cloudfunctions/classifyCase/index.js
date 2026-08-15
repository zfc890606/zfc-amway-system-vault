// 云函数：classifyCase — AI 自动归类 + 起标题 + 提取字段
// 通过 OpenAI 兼容接口调用大模型（默认 DeepSeek，可换通义/豆包）
// 配置方式二选一：
//   1. 在云函数「环境变量」里配置 AI_API_KEY / AI_API_BASE / AI_MODEL（推荐，密钥不落代码）
//   2. 直接改下面 CONFIG 默认值
const cloud = require('wx-server-sdk')
const https = require('https')

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })

const CONFIG = {
  apiBase: process.env.AI_API_BASE || 'https://api.deepseek.com/v1',
  apiKey: process.env.AI_API_KEY || '在这里填入你的API_KEY',
  model: process.env.AI_MODEL || 'deepseek-chat'
}

const SYSTEM_PROMPT = `你是张医生团队（AI营养师）的慢病案例库分类助手。请把用户上传的案例记录自动归类。

输出要求：只输出一个 JSON 对象，不要输出任何其他文字。字段如下：
{
  "category": "板块，只能取以下之一：肥胖 / 痛风 / 糖尿病 / 高血压 / 免疫 / 症状管理 / 其他",
  "title": "醒目标题，格式：板块·人群·关键指标变化·时长。例如「痛风·男42岁·尿酸620→380·3个月复盘」",
  "tags": ["2到4个关键词标签"],
  "alias": "客户化名，如果文本里有称呼（如王先生/李女士）就用，没有则留空字符串",
  "ageRange": "年龄段，如 40-50岁，没有则留空字符串",
  "sex": "男/女，没有则留空字符串",
  "chiefComplaint": "主诉与背景，2-3句话概括客户的问题",
  "metrics": {"指标名": "变化描述"}，如 {"尿酸": "620→380", "体重": "85→72kg"}，没有则空对象,
  "metricsText": "检查指标变化的一句话描述，如「尿酸 620→380；体重 85→72kg」"
}

注意：
- 这是生活方式干预案例复盘，不是医疗诊断，不要写疗效承诺
- 客户姓名一律只取称呼（先生/女士）或化名，不存全名
- 如果内容判断不了板块，用「其他」`

function chatCompletion(messages) {
  const url = new URL(CONFIG.apiBase.replace(/\/$/, '') + '/chat/completions')
  const payload = JSON.stringify({
    model: CONFIG.model,
    messages,
    temperature: 0.3
  })
  const options = {
    hostname: url.hostname,
    path: url.pathname + url.search,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + CONFIG.apiKey,
      'Content-Length': Buffer.byteLength(payload)
    },
    timeout: 30000
  }
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = ''
      res.on('data', (chunk) => { data += chunk })
      res.on('end', () => {
        try {
          const json = JSON.parse(data)
          if (json.error) {
            reject(new Error(json.error.message || 'AI接口错误'))
            return
          }
          resolve(json)
        } catch (e) {
          reject(new Error('AI响应解析失败：' + data.slice(0, 200)))
        }
      })
    })
    req.on('timeout', () => { req.destroy(); reject(new Error('AI接口超时')) })
    req.on('error', reject)
    req.write(payload)
    req.end()
  })
}

function extractJson(content) {
  try {
    return JSON.parse(content)
  } catch (e) {
    // 容错：尝试从返回文本里抠出第一个 { } 块
    const m = content.match(/\{[\s\S]*\}/)
    if (m) return JSON.parse(m[0])
    throw new Error('AI没有返回可解析的JSON')
  }
}

exports.main = async (event) => {
  const text = (event.text || '').trim()
  if (text.length < 10) {
    return { ok: false, message: '案例内容太短，无法归类' }
  }
  if (CONFIG.apiKey.indexOf('你的API_KEY') !== -1 || CONFIG.apiKey === '') {
    return { ok: false, message: '请先在云函数 classifyCase 的环境变量里配置 AI_API_KEY' }
  }
  try {
    const resp = await chatCompletion([
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: text }
    ])
    const content = resp.choices && resp.choices[0] && resp.choices[0].message.content
    if (!content) return { ok: false, message: 'AI没有返回内容' }
    const parsed = extractJson(content)
    // 校验板块，非法值兜底为「其他」
    const VALID = ['肥胖', '痛风', '糖尿病', '高血压', '免疫', '症状管理', '其他']
    if (!VALID.includes(parsed.category)) parsed.category = '其他'
    if (!Array.isArray(parsed.tags)) parsed.tags = []
    if (!parsed.title) parsed.title = parsed.category + ' · 案例复盘'
    return { ok: true, data: parsed }
  } catch (err) {
    return { ok: false, message: 'AI 归类失败：' + err.message }
  }
}
