// 云函数：updateCase — 更新案例（团队内可编辑）
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const id = event.id
  const payload = event.payload || {}
  if (!id) return { ok: false, message: '缺少案例ID' }

  // 白名单字段，防止覆盖系统字段
  const allowed = ['title', 'category', 'alias', 'ageRange', 'chiefComplaint', 'metrics', 'plan', 'result', 'tags']
  const clean = {}
  allowed.forEach(k => {
    if (payload[k] !== undefined) clean[k] = payload[k]
  })
  clean.updatedAt = Date.now()

  const res = await db.collection('cases').doc(id).update({ data: clean })
  return { ok: true, data: { updated: res.stats.updated } }
}
