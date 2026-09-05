// 我的 — 个人日历格 + 统计 + 最近打卡明细 + 改昵称 + 邀请码（仅发起人）
const { getPlan, getMyCheckins, updateNickname } = require('../../utils/api')
const { dayNo, getToday } = require('../../utils/date')
const { formatTime, formatClock } = require('../../utils/format')

Page({
  data: {
    planName: '',
    isOwner: false,
    inviteCode: '',
    nickname: '',
    initial: '',
    joinedAtText: '',
    currentStreak: 0,
    bestStreak: 0,
    totalDays: 0,
    fullDays: 0,
    dayStatus: [],
    todayIdx: -1,
    checkins: [],
    loading: true
  },

  onShow() {
    this.init()
  },

  onPullDownRefresh() {
    this.init().finally(() => wx.stopPullDownRefresh())
  },

  async init() {
    try {
      const route = await getPlan()
      if (!route.plan) {
        wx.reLaunch({ url: '/pages/create/create' })
        return
      }
      if (!route.joined) {
        wx.reLaunch({ url: '/pages/join/join' })
        return
      }
      const mine = await getMyCheckins(route.plan._id)
      const member = mine.member || {}
      const isOwner = route.plan.ownerOpenid === route.member.openid
      const todayIdx = Math.max(0, Math.min(179, dayNo(route.plan.startDate, getToday()) - 1))

      const checkins = (mine.checkins || []).map(c => {
        const morning = c.morning ? { ...c.morning, timeText: formatClock(c.morning.time) } : null
        const evening = c.evening ? { ...c.evening, timeText: formatClock(c.evening.time) } : null
        return {
          ...c,
          morning,
          evening,
          dateText: c.date
        }
      })

      this.setData({
        planName: route.plan.name,
        isOwner,
        inviteCode: isOwner ? (route.plan.inviteCode || '') : '',
        nickname: member.nickname || '',
        initial: (member.nickname || '我')[0],
        joinedAtText: member.joinedAt ? formatTime(member.joinedAt) : '',
        currentStreak: member.currentStreak || 0,
        bestStreak: member.bestStreak || 0,
        totalDays: member.totalDays || 0,
        fullDays: member.fullDays || 0,
        dayStatus: Array.isArray(member.dayStatus) ? member.dayStatus : [],
        todayIdx,
        checkins,
        loading: false
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
      this.setData({ loading: false })
    }
  },

  onChangeNickname() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '输入新昵称（1-12 字）',
      content: this.data.nickname,
      success: async (res) => {
        if (res.confirm && res.content && res.content.trim()) {
          const nickname = res.content.trim()
          if (nickname.length > 12) {
            wx.showToast({ title: '昵称最长 12 个字', icon: 'none' })
            return
          }
          try {
            await updateNickname({ nickname })
            wx.showToast({ title: '昵称已更新', icon: 'none' })
            this.init()
          } catch (e) {
            wx.showToast({ title: e.message, icon: 'none' })
          }
        }
      }
    })
  },

  onCopyCode() {
    if (!this.data.inviteCode) return
    wx.setClipboardData({
      data: this.data.inviteCode,
      success: () => {
        wx.showToast({ title: '邀请码已复制', icon: 'none' })
      }
    })
  },

  onPreview(e) {
    const url = e.currentTarget.dataset.url
    if (url) {
      wx.previewImage({ urls: [url] })
    }
  }
})
