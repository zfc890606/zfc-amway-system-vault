// 云函数：joinPlan — 通过邀请码加入计划
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const inviteCode = String(event.inviteCode || '').trim().toUpperCase()
  const nickname = String(event.nickname || '').trim()

  if (!inviteCode) return { ok: false, message: '请输入邀请码' }
  if (!nickname || nickname.length > 12) return { ok: false, message: '昵称需为1-12个字符' }

  const planRes = await db.collection('plans').where({ inviteCode }).limit(1).get()
  if (!planRes.data.length) return { ok: false, message: '邀请码不正确' }
  const plan = planRes.data[0]

  // 幂等：已加入则直接返回成功
  const memberRes = await db.collection('members').where({ planId: plan._id, openid: OPENID }).limit(1).get()
  if (memberRes.data.length) {
    return { ok: true, data: { planId: plan._id, joined: true, already: true } }
  }

  const now = Date.now()
  const memberDoc = {
    planId: plan._id,
    openid: OPENID,
    nickname,
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

  return { ok: true, data: { planId: plan._id, joined: true, already: false } }
}
