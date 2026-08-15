// 云函数：stats — 统计各板块案例数
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const _ = db.command

exports.main = async () => {
  const { OPENID } = cloud.getWXContext()
  const $ = db.command.aggregate

  const agg = await db.collection('cases').aggregate()
    .match({ deleted: false })
    .group({ _id: '$category', count: $.sum(1) })
    .end()

  const counts = {}
  let total = 0
  agg.list.forEach(g => {
    counts[g._id] = g.count
    total += g.count
  })

  const mine = await db.collection('cases')
    .where({ deleted: false, openid: OPENID })
    .count()

  return { ok: true, data: { total, counts, myCount: mine.total } }
}
