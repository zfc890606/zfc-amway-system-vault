// 云函数：addCase — 新增案例（云函数拥有管理员权限，不走数据库客户端权限）
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const payload = event.payload || {}
  const now = Date.now()

  const doc = {
    title: String(payload.title || '').trim(),
    category: String(payload.category || '其他'),
    alias: String(payload.alias || '').trim(),
    ageRange: String(payload.ageRange || '').trim(),
    chiefComplaint: String(payload.chiefComplaint || ''),
    metrics: String(payload.metrics || ''),
    plan: String(payload.plan || ''),
    result: String(payload.result || ''),
    tags: Array.isArray(payload.tags) ? payload.tags : [],
    openid: OPENID,
    deleted: false,
    createdAt: now,
    updatedAt: now
  }

  if (!doc.title) return { ok: false, message: '标题不能为空' }

  const res = await db.collection('cases').add({ data: doc })
  return { ok: true, data: { _id: res._id } }
}
