// 云函数：getMyCheckins — 我的成员信息 + 最近打卡明细
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const planId = String(event.planId || '')
  if (!planId) return { ok: false, message: '参数不完整' }

  const memberRes = await db.collection('members').where({ planId, openid: OPENID }).limit(1).get()
  if (!memberRes.data.length) return { ok: false, message: '你还没加入该计划' }
  const member = memberRes.data[0]

  const checkinRes = await db.collection('checkins')
    .where({ planId, openid: OPENID })
    .orderBy('date', 'desc')
    .limit(50)
    .get()

  return {
    ok: true,
    data: {
      member: {
        nickname: member.nickname,
        joinedAt: member.joinedAt,
        dayStatus: Array.isArray(member.dayStatus) ? member.dayStatus : new Array(180).fill(0),
        currentStreak: member.currentStreak || 0,
        bestStreak: member.bestStreak || 0,
        totalDays: member.totalDays || 0,
        fullDays: member.fullDays || 0,
        lastCheckinDate: member.lastCheckinDate || ''
      },
      checkins: (checkinRes.data || []).map(c => ({
        id: c._id,
        date: c.date,
        dayNo: c.dayNo,
        morning: c.morning || null,
        evening: c.evening || null,
        updatedAt: c.updatedAt
      }))
    }
  }
}
