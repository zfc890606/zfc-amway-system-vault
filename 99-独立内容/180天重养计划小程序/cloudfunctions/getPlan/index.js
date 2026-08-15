// 云函数：getPlan — 我的计划状态（路由判断用）
// 返回 { plan, member, joined }
//  - 已加入：plan（发起人含 inviteCode）+ member
//  - 未加入但已存在计划：plan（不含 inviteCode）+ joined:false
//  - 还没有任何计划：plan:null
const cloud = require('wx-server-sdk')
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV })
const db = cloud.database()

function stripCode(plan) {
  if (!plan) return plan
  const { inviteCode, ...rest } = plan
  return rest
}

exports.main = async () => {
  const { OPENID } = cloud.getWXContext()

  // ① 找我的成员记录
  const memberRes = await db.collection('members').where({ openid: OPENID }).limit(1).get()
  if (memberRes.data.length) {
    const member = memberRes.data[0]
    const planRes = await db.collection('plans').where({ _id: member.planId }).limit(1).get()
    if (!planRes.data.length) {
      return { ok: true, data: { plan: null, member: null, joined: false } }
    }
    const plan = planRes.data[0]
    const isOwner = plan.ownerOpenid === OPENID
    return { ok: true, data: { plan: isOwner ? plan : stripCode(plan), member, joined: true } }
  }

  // ② 未加入：返回最近的计划（不含邀请码），或 null
  const planRes = await db.collection('plans').orderBy('createdAt', 'desc').limit(1).get()
  if (!planRes.data.length) {
    return { ok: true, data: { plan: null, member: null, joined: false } }
  }
  return { ok: true, data: { plan: stripCode(planRes.data[0]), member: null, joined: false } }
}
