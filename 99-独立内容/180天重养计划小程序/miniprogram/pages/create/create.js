// 创建页 — 发起人首次进入
const { createPlan, getPlan } = require('../../utils/api')
const { getToday } = require('../../utils/date')

Page({
  data: {
    name: '',
    startDate: '',
    nickname: '',
    submitting: false
  },

  onLoad() {
    this.setData({ startDate: getToday() })
  },

  onShow() {
    // 已加入计划的用户不应看到创建页（防误入）
    if (this._checked) return
    this._checked = true
    getPlan().then(d => {
      if (d.joined) {
        wx.reLaunch({ url: '/pages/index/index' })
      }
    }).catch(() => {})
  },

  onName(e) {
    this.setData({ name: e.detail.value })
  },

  onStartDate(e) {
    this.setData({ startDate: e.detail.value })
  },

  onNickname(e) {
    this.setData({ nickname: e.detail.value })
  },

  async onSubmit() {
    if (this.data.submitting) return
    const name = this.data.name.trim()
    const nickname = this.data.nickname.trim()
    if (!name) {
      wx.showToast({ title: '请填写计划名称', icon: 'none' })
      return
    }
    if (!nickname) {
      wx.showToast({ title: '请填写你的昵称', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    try {
      const data = await createPlan({
        name,
        startDate: this.data.startDate,
        ownerNickname: nickname
      })
      wx.showModal({
        title: '计划创建成功 🎉',
        content: `你的邀请码：${data.inviteCode}\n\n把它发给伙伴，一起加入「${name}」，互相陪伴 180 天。`,
        showCancel: false,
        confirmText: '进入工作台',
        success: () => {
          wx.reLaunch({ url: '/pages/index/index' })
        }
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ submitting: false })
  }
})
