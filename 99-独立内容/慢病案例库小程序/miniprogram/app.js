// app.js — 慢病案例库
App({
  onLaunch() {
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
    } else {
      wx.cloud.init({
        // ⚠️ 改成你自己的云环境ID（微信开发者工具 → 云开发 → 环境ID）
        env: '你的云环境ID',
        traceUser: true
      })
    }
    this.globalData = {}
  }
})
