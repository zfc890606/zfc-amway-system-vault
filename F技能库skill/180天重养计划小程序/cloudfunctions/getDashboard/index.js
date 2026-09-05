// 云函数：getDashboard — 工作台聚合数据（只查2次库）
// ① members 按 currentStreak 倒序全拉（≤50人） ② 今日 checkins 按 updatedAt 倒序
// feed / leaderboard / stats / 阶段趋势 全部内存计算
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

function pad(n) {
  return n < 10 ? '0' + n : '' + n
}

function todayStr() {
  const d = new Date(Date.now() + 8 * 3600 * 1000)
  return `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`
}

function dayDiff(a, b) {
  const pa = a.split('-').map(Number)
  const pb = b.split('-').map(Number)
  return (Date.UTC(pb[0], pb[1] - 1, pb[2]) - Date.UTC(pa[0], pa[1] - 1, pa[2])) / 86400000
}

exports.main = async (event) => {
  const planId = String(event.planId || '')
  if (!planId) return { ok: false, message: '参数不完整' }

  // ① 成员（排行榜源数据，含 dayStatus 供日历格）
  const memberRes = await db.collection('members')
    .where({ planId })
    .orderBy('currentStreak', 'desc')
    .limit(50)
    .get()

  // ② 今日动态
  const today = todayStr()
  const feedRes = await db.collection('checkins')
    .where({ planId, date: today })
    .orderBy('updatedAt', 'desc')
    .limit(100)
    .get()

  const planRes = await db.collection('plans').where({ _id: planId }).limit(1).get()
  if (!planRes.data.length) return { ok: false, message: '计划不存在' }
  const plan = planRes.data[0]

  const members = memberRes.data || []
  const memberCount = members.length
  const todayDayNo = Math.max(1, Math.min(180, dayDiff(plan.startDate, today) + 1))
  const elapsedDays = todayDayNo // 已过的天数（含今天）

  // 昵称映射（feed 用）
  const nickMap = {}
  members.forEach(m => { nickMap[m.openid] = m.nickname })

  // 今日动态
  const todayFeed = (feedRes.data || []).map(c => ({
    id: c._id,
    openid: c.openid,
    nickname: nickMap[c.openid] || '伙伴',
    dayNo: c.dayNo,
    date: c.date,
    morning: c.morning || null,
    evening: c.evening || null,
    updatedAt: c.updatedAt
  }))

  // 照片：云函数统一转临时链接（存储权限无需"所有用户可读"，
  // 别人照片也能在共享工作台加载）
  const photoIDs = []
  todayFeed.forEach(f => {
    if (f.morning && f.morning.photo) photoIDs.push(f.morning.photo)
    if (f.evening && f.evening.photo) photoIDs.push(f.evening.photo)
  })
  const uniqueIDs = [...new Set(photoIDs)]
  let urlMap = {}
  if (uniqueIDs.length) {
    const urlRes = await cloud.getTempFileURL({ fileList: uniqueIDs })
    ;(urlRes.fileList || []).forEach(item => {
      if (item.status === 0 && item.tempFileURL) {
        urlMap[item.fileID] = item.tempFileURL
      }
    })
  }
  todayFeed.forEach(f => {
    if (f.morning && f.morning.photo && urlMap[f.morning.photo]) {
      f.morning = { ...f.morning, photo: urlMap[f.morning.photo] }
    }
    if (f.evening && f.evening.photo && urlMap[f.evening.photo]) {
      f.evening = { ...f.evening, photo: urlMap[f.evening.photo] }
    }
  })

  // 成员视图（供日历格 + 排行榜 + 成员切换）
  const memberViews = members.map(m => ({
    openid: m.openid,
    nickname: m.nickname,
    dayStatus: Array.isArray(m.dayStatus) && m.dayStatus.length === 180 ? m.dayStatus : new Array(180).fill(0),
    currentStreak: m.currentStreak || 0,
    bestStreak: m.bestStreak || 0,
    totalDays: m.totalDays || 0,
    fullDays: m.fullDays || 0
  }))

  // 排行榜 top20（已在库内按 currentStreak 倒序）
  const leaderboard = memberViews.slice(0, 20).map((m, i) => ({
    rank: i + 1,
    nickname: m.nickname,
    currentStreak: m.currentStreak,
    bestStreak: m.bestStreak,
    totalDays: m.totalDays,
    fullDays: m.fullDays
  }))

  // 完成率（严格口径：早晚都打 = 1 个 fullDay）
  const totalFullDays = members.reduce((s, m) => s + (m.fullDays || 0), 0)
  const completionRate = memberCount && elapsedDays > 0
    ? Math.round(totalFullDays / (memberCount * elapsedDays) * 1000) / 10
    : 0

  // 6阶段趋势（每30天一段，内存计算）
  const phaseTrend = []
  for (let p = 1; p <= 6; p++) {
    const phaseStart = (p - 1) * 30 + 1
    const phaseDays = Math.max(0, Math.min(30, elapsedDays - phaseStart + 1))
    let phaseFull = 0
    members.forEach(m => {
      if (!Array.isArray(m.dayStatus)) return
      for (let i = phaseStart - 1; i < phaseStart - 1 + phaseDays; i++) {
        if (m.dayStatus[i] === 3) phaseFull++
      }
    })
    const rate = memberCount && phaseDays > 0
      ? Math.round(phaseFull / (memberCount * phaseDays) * 1000) / 10
      : 0
    phaseTrend.push({ phase: p, rate })
  }

  return {
    ok: true,
    data: {
      plan: {
        _id: plan._id,
        name: plan.name,
        startDate: plan.startDate,
        ownerNickname: plan.ownerNickname,
        totalDays: plan.totalDays
      },
      today,
      todayDayNo,
      elapsedDays,
      memberCount,
      members: memberViews,
      todayFeed,
      leaderboard,
      completionRate,
      phaseTrend
    }
  }
}
