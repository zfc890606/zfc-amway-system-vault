// 云函数：deleteCase — 软删除案例
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const id = event.id
  if (!id) return { ok: false, message: '缺少案例ID' }
  await db.collection('cases').doc(id).update({
    data: { deleted: true, updatedAt: Date.now() }
  })
  return { ok: true, data: {} }
}
