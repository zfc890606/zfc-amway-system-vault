// 云函数：listCases — 按板块/关键词分页查询案例
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()
const _ = db.command

exports.main = async (event) => {
  const category = event.category || ''
  const keyword = (event.keyword || '').trim()
  const page = Number(event.page || 0)
  const pageSize = Math.min(Number(event.pageSize || 100), 100)

  const conds = [{ deleted: false }]
  if (category) conds.push({ category })

  if (keyword) {
    const reg = db.RegExp({ regexp: keyword, options: 'i' })
    conds.push(_.or([
      { title: reg },
      { chiefComplaint: reg },
      { metrics: reg },
      { result: reg }
    ]))
  }

  const where = _.and(conds)

  const res = await db.collection('cases')
    .where(where)
    .orderBy('updatedAt', 'desc')
    .skip(page * pageSize)
    .limit(pageSize)
    .get()

  return { ok: true, data: res.data }
}
