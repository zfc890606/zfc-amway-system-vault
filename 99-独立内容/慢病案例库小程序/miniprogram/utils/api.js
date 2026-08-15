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
  // AI 自动归类 + 起标题
  classifyCase: (text) => callFunction('classifyCase', { text }),
  // 新增案例
  addCase: (payload) => callFunction('addCase', { payload }),
  // 列表查询（category 空=全部；keyword 空=不过滤）
  listCases: (filter = {}) => callFunction('listCases', filter),
  // 详情
  getCase: (id) => callFunction('getCase', { id }),
  // 更新
  updateCase: (id, payload) => callFunction('updateCase', { id, payload }),
  // 删除（软删除）
  deleteCase: (id) => callFunction('deleteCase', { id }),
  // 统计
  stats: () => callFunction('stats')
}
