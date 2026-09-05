// app.js — 180天重养计划
App({
  onLaunch() {
    if (!wx.cloud) {
      console.error('请使用 2.2.3 或以上的基础库以使用云能力')
    } else {
      wx.cloud.init({
        // ⚠️ 云环境ID（微信开发者工具 → 云开发 → 环境ID）
        env: 'cloud1-d9goyt54f762f742f',
        traceUser: true
      })
    }
    this.globalData = {}
  }
})
