// 云函数调用统一封装
// 所有读写都走云函数（云函数拥有管理员权限），小程序端不直接碰数据库，权限更安全

function callFunction(name, data = {}) {
  return wx.cloud.callFunction({ name, data }).then(res => {
    const result = res.result || {}
    if (result.ok) return result.data
    throw new Error(result.message || '调用失败')
  }).catch(err => {
    // 兼容网络层错误
    throw new Error(err.message || '网络错误，请重试')
  })
}

module.exports = {
  // 创建计划（发起人）
  createPlan: (payload) => callFunction('createPlan', payload),
  // 加入计划（邀请码+昵称）
  joinPlan: (payload) => callFunction('joinPlan', payload),
  // 我的计划状态（路由判断：null→创建 / joined=false→加入 / joined=true→正常）
  getPlan: () => callFunction('getPlan', {}),
  // 提交打卡（morning / evening）
  submitCheckin: (payload) => callFunction('submitCheckin', payload),
  // 工作台聚合数据（feed + 成员 + 排行榜 + 统计）
  getDashboard: (planId) => callFunction('getDashboard', { planId }),
  // 我的打卡明细
  getMyCheckins: (planId) => callFunction('getMyCheckins', { planId }),
  // 修改昵称
  updateNickname: (payload) => callFunction('updateNickname', payload)
}
