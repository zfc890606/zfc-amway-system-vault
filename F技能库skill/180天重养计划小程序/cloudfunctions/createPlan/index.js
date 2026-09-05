// 云函数：createPlan — 创建计划（发起人）
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

// 邀请码字符集：去掉易混的 0/O/1/I
const CODE_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

function genCode(len = 6) {
  let s = ''
  for (let i = 0; i < len; i++) {
    s += CODE_CHARS[Math.floor(Math.random() * CODE_CHARS.length)]
  }
  return s
}

// 生成不重复的邀请码
async function uniqueCode() {
  for (let i = 0; i < 10; i++) {
    const code = genCode()
    const res = await db.collection('plans').where({ inviteCode: code }).count()
    if (res.total === 0) return code
  }
  throw new Error('生成邀请码失败，请重试')
}

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const name = String(event.name || '').trim()
  const startDate = String(event.startDate || '')
  const ownerNickname = String(event.ownerNickname || '').trim()

  if (!name) return { ok: false, message: '请填写计划名称' }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(startDate)) return { ok: false, message: '开始日期格式不正确' }
  if (!ownerNickname || ownerNickname.length > 12) return { ok: false, message: '昵称需为1-12个字符' }

  const now = Date.now()
  const inviteCode = await uniqueCode()

  const planDoc = {
    name,
    inviteCode,
    startDate,
    totalDays: 180,
    phaseCount: 6,
    daysPerPhase: 30,
    ownerOpenid: OPENID,
    ownerNickname,
    createdAt: now
  }
  const res = await db.collection('plans').add({ data: planDoc })
  const planId = res._id

  // 发起人自动成为第一个成员
  const memberDoc = {
    planId,
    openid: OPENID,
    nickname: ownerNickname,
    joinedAt: now,
    dayStatus: new Array(180).fill(0),
    currentStreak: 0,
    bestStreak: 0,
    totalDays: 0,
    fullDays: 0,
    lastCheckinDate: '',
    updatedAt: now
  }
  await db.collection('members').add({ data: memberDoc })

  return { ok: true, data: { planId, inviteCode } }
}
