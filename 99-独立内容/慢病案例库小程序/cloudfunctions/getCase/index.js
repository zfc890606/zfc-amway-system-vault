// 云函数：getCase — 案例详情
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const id = event.id
  if (!id) return { ok: false, message: '缺少案例ID' }
  try {
    const res = await db.collection('cases').doc(id).get()
    return { ok: true, data: res.data }
  } catch (e) {
    return { ok: false, message: '案例不存在' }
  }
}
