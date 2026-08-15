// 加入页 — 邀请码 + 昵称
const { joinPlan, getPlan } = require('../../utils/api')

Page({
  data: {
    planName: '',
    inviteCode: '',
    nickname: '',
    submitting: false
  },

  onShow() {
    // 已加入则直接进工作台
    getPlan().then(d => {
      if (d.joined) {
        wx.reLaunch({ url: '/pages/index/index' })
        return
      }
      if (d.plan) {
        this.setData({ planName: d.plan.name })
      }
    }).catch(() => {})
  },

  onCode(e) {
    this.setData({ inviteCode: e.detail.value.toUpperCase() })
  },

  onNickname(e) {
    this.setData({ nickname: e.detail.value })
  },

  async onSubmit() {
    if (this.data.submitting) return
    const inviteCode = this.data.inviteCode.trim().toUpperCase()
    const nickname = this.data.nickname.trim()
    if (!inviteCode) {
      wx.showToast({ title: '请输入邀请码', icon: 'none' })
      return
    }
    if (!nickname) {
      wx.showToast({ title: '请填写昵称', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    try {
      await joinPlan({ inviteCode, nickname })
      wx.showToast({ title: '加入成功 🎉', icon: 'none' })
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/index/index' })
      }, 600)
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ submitting: false })
  }
})
