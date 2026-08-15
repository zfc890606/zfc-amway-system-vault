// 云函数：submitCheckin — 提交打卡（早/晚）
// 去重三重防线：确定性 _id + slot 已存在拒绝 + add 重复键异常兜底
// 宽容口径：当天任一时段打卡即算当天有（用于排行榜）
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

function pad(n) {
  return n < 10 ? '0' + n : '' + n
}

// 北京时间"今天"（服务器时区无关）
function todayStr() {
  const d = new Date(Date.now() + 8 * 3600 * 1000)
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`
}

// 天数差值（Date.UTC 求差，避免时区坑）
function dayDiff(a, b) {
  const pa = a.split('-').map(Number)
  const pb = b.split('-').map(Number)
  return (Date.UTC(pb[0], pb[1] - 1, pb[2]) - Date.UTC(pa[0], pa[1] - 1, pa[2])) / 86400000
}

// 连续打卡天数：从今天（或最近打卡日）往前数连续天
function calcStreak(dayStatus, todayDayNo) {
  let i = todayDayNo - 1
  if (i >= 0 && dayStatus[i] === 0) i-- // 今天还没打，从昨天开始数
  let streak = 0
  while (i >= 0) {
    if (dayStatus[i] > 0) {
      streak++
      i--
    } else {
      break
    }
  }
  return streak
}

function slotLabel(slot) {
  return slot === 'morning' ? '早' : '晚'
}

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const planId = String(event.planId || '')
  const date = String(event.date || '')
  const slot = String(event.slot || '')
  const photo = String(event.photo || '').trim()
  const text = String(event.text || '').trim().slice(0, 200)

  if (!planId || !/^\d{4}-\d{2}-\d{2}$/.test(date)) return { ok: false, message: '参数不完整' }
  if (slot !== 'morning' && slot !== 'evening') return { ok: false, message: '打卡时段不正确' }

  const memberRes = await db.collection('members').where({ planId, openid: OPENID }).limit(1).get()
  if (!memberRes.data.length) return { ok: false, message: '你还没加入该计划' }
  const member = memberRes.data[0]

  const planRes = await db.collection('plans').where({ _id: planId }).limit(1).get()
  if (!planRes.data.length) return { ok: false, message: '计划不存在' }
  const plan = planRes.data[0]

  // 日期边界校验：计划内 + 不能预打卡
  const today = todayStr()
  const d = dayDiff(plan.startDate, date)
  if (d < 0) return { ok: false, message: '计划还没开始' }
  if (d >= plan.totalDays) return { ok: false, message: '超出计划天数' }
  if (date > today) return { ok: false, message: '不能预打卡' }
  const dayNo = d + 1
  const idx = dayNo - 1

  const _id = `${planId}_${OPENID}_${date}`
  const now = Date.now()
  const slotValue = { photo, text, time: now }

  // 确定性 _id：一天一人一条
  const existing = await db.collection('checkins').where({ _id }).limit(1).get()

  if (existing.data.length) {
    const doc = existing.data[0]
    if (doc[slot]) {
      return { ok: false, message: `今天的${slotLabel(slot)}打卡已完成` }
    }
    await db.collection('checkins').doc(_id).update({
      data: { [slot]: slotValue, updatedAt: now }
    })
  } else {
    const doc = {
      _id, planId, openid: OPENID, date, dayNo,
      morning: null, evening: null,
      createdAt: now, updatedAt: now
    }
    doc[slot] = slotValue
    try {
      await db.collection('checkins').add({ data: doc })
    } catch (e) {
      // 并发重复 add：兜底走 update
      const dup = await db.collection('checkins').where({ _id }).limit(1).get()
      if (dup.data.length) {
        if (dup.data[0][slot]) {
          return { ok: false, message: `今天的${slotLabel(slot)}打卡已完成` }
        }
        await db.collection('checkins').doc(_id).update({
          data: { [slot]: slotValue, updatedAt: now }
        })
      } else {
        throw e
      }
    }
  }

  // 重算成员聚合字段
  const dayStatus = Array.isArray(member.dayStatus) && member.dayStatus.length === 180
    ? member.dayStatus.slice()
    : new Array(180).fill(0)
  dayStatus[idx] = (dayStatus[idx] || 0) | (slot === 'morning' ? 1 : 2)

  const totalDays = dayStatus.filter(v => v > 0).length
  const fullDays = dayStatus.filter(v => v === 3).length
  const currentStreak = calcStreak(dayStatus, dayNo)
  const bestStreak = Math.max(member.bestStreak || 0, currentStreak)
  const lastCheckinDate = !member.lastCheckinDate || date > member.lastCheckinDate
    ? date
    : member.lastCheckinDate

  await db.collection('members').doc(member._id).update({
    data: {
      dayStatus,
      totalDays,
      fullDays,
      currentStreak,
      bestStreak,
      lastCheckinDate,
      updatedAt: now
    }
  })

  return {
    ok: true,
    data: {
      dayNo, slot,
      currentStreak, bestStreak, totalDays, fullDays
    }
  }
}
