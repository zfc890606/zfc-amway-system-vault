// 工作台 — 四模块：今日动态 / 180天日历格 / 连续打卡排行榜 / 完成率统计
const { getPlan, getDashboard } = require('../../utils/api')
const { getPhase, getTip } = require('../../utils/content')

const POLL_MS = 30000

const TREND_COLORS = {
  1: '#7BC47F',
  2: '#4FC1E9',
  3: '#A58BDB',
  4: '#F5A623',
  5: '#E86A8C',
  6: '#F7C948'
}

Page({
  data: {
    loading: true,
    planName: '',
    startDate: '',
    ownerNickname: '',
    todayDayNo: 0,
    phase: null,
    tip: '',
    feed: [],
    members: [],
    activeOpenid: '',
    activeMember: null,
    leaderboard: [],
    completionRate: 0,
    phaseTrend: [],
    memberCount: 0,
    elapsedDays: 0,
    myOpenid: ''
  },

  onShow() {
    this.init()
    this.startPoll()
  },

  onHide() {
    this.stopPoll()
  },

  onUnload() {
    this.stopPoll()
  },

  onPullDownRefresh() {
    this.refreshDashboard().finally(() => wx.stopPullDownRefresh())
  },

  startPoll() {
    this.stopPoll()
    this.timer = setInterval(() => this.refreshDashboard(), POLL_MS)
  },

  stopPoll() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
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
      this.planId = route.plan._id
      this.myOpenid = route.member.openid
      await this.refreshDashboard()
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
      this.setData({ loading: false })
    }
  },

  async refreshDashboard() {
    if (!this.planId) return
    try {
      const d = await getDashboard(this.planId)

      // 默认选中自己，找不到则选排行第一
      let activeOpenid = this.data.activeOpenid
      if (!activeOpenid || !d.members.some(m => m.openid === activeOpenid)) {
        activeOpenid = d.members.some(m => m.openid === this.myOpenid)
          ? this.myOpenid
          : (d.members.length ? d.members[0].openid : '')
      }
      const activeMember = d.members.find(m => m.openid === activeOpenid) || null

      this.setData({
        loading: false,
        planName: d.plan.name,
        startDate: d.plan.startDate,
        ownerNickname: d.plan.ownerNickname,
        todayDayNo: d.todayDayNo,
        phase: getPhase(d.todayDayNo),
        tip: getTip(d.todayDayNo),
        feed: d.todayFeed,
        members: d.members,
        activeOpenid,
        activeMember,
        leaderboard: d.leaderboard,
        completionRate: d.completionRate,
        phaseTrend: d.phaseTrend.map(p => ({ ...p, color: TREND_COLORS[p.phase] || '#EEEEEE' })),
        memberCount: d.memberCount,
        elapsedDays: d.elapsedDays
      })
    } catch (e) {
      // 轮询失败保持静默，不打断用户
      if (this.data.loading) {
        this.setData({ loading: false })
      }
    }
  },

  onSwitchMember(e) {
    const openid = e.currentTarget.dataset.openid
    const activeMember = this.data.members.find(m => m.openid === openid) || null
    this.setData({ activeOpenid: openid, activeMember })
  },

  onPreview(e) {
    const url = e.currentTarget.dataset.url
    if (url) {
      wx.previewImage({ urls: [url] })
    }
  }
})
