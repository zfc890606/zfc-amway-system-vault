// 云函数：updateNickname — 修改我的昵称（成员表 + 发起人同步更新计划表）
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

exports.main = async (event) => {
  const { OPENID } = cloud.getWXContext()
  const nickname = String(event.nickname || '').trim()

  if (!nickname || nickname.length > 12) return { ok: false, message: '昵称需为1-12个字符' }

  const memberRes = await db.collection('members').where({ openid: OPENID }).limit(1).get()
  if (!memberRes.data.length) return { ok: false, message: '你还未加入计划' }
  const member = memberRes.data[0]

  const now = Date.now()
  await db.collection('members').doc(member._id).update({
    data: { nickname, updatedAt: now }
  })

  // 发起人改昵称时，同步计划里的 ownerNickname（看板显示发起人名字）
  const planRes = await db.collection('plans').where({ _id: member.planId }).limit(1).get()
  if (planRes.data.length && planRes.data[0].ownerOpenid === OPENID) {
    await db.collection('plans').doc(member.planId).update({
      data: { ownerNickname: nickname, updatedAt: now }
    })
  }

  return { ok: true, data: { nickname } }
}
