// 打卡页 — 早晚各一次，拍照打卡（可配文字）
const { getPlan, getMyCheckins, submitCheckin } = require('../../utils/api')
const { getPhase, getTip } = require('../../utils/content')
const { getToday, dayNo } = require('../../utils/date')
const { formatClock } = require('../../utils/format')

Page({
  data: {
    planName: '',
    today: '',
    dayNo: 0,
    phase: null,
    tip: '',
    beforeStart: false,
    afterEnd: false,
    waitDays: 0,
    slot: 'morning',
    isDone: false,
    morningDone: false,
    eveningDone: false,
    morning: null,
    evening: null,
    photoTemp: '',
    text: '',
    submitting: false
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
      const today = getToday()
      const dn = dayNo(route.plan.startDate, today)
      const beforeStart = dn < 1
      const afterEnd = dn > 180

      this.planId = route.plan._id
      let morning = null
      let evening = null
      let morningDone = false
      let eveningDone = false

      if (!beforeStart && !afterEnd) {
        const status = (route.member.dayStatus || [])[dn - 1] || 0
        morningDone = (status & 1) === 1
        eveningDone = (status & 2) === 2
        if (status > 0) {
          const mine = await getMyCheckins(this.planId)
          const todayCheckin = (mine.checkins || []).find(c => c.date === today) || null
          if (todayCheckin) {
            morning = todayCheckin.morning || null
            evening = todayCheckin.evening || null
            if (morning && morning.time) morning = { ...morning, timeText: formatClock(morning.time) }
            if (evening && evening.time) evening = { ...evening, timeText: formatClock(evening.time) }
          }
        }
      }

      const slot = morningDone ? 'evening' : 'morning'
      const isDone = slot === 'morning' ? morningDone : eveningDone

      this.setData({
        planName: route.plan.name,
        today,
        dayNo: dn,
        phase: getPhase(dn),
        tip: getTip(dn),
        beforeStart,
        afterEnd,
        waitDays: beforeStart ? 1 - dn : 0,
        slot,
        isDone,
        morningDone,
        eveningDone,
        morning,
        evening,
        photoTemp: '',
        text: '',
        submitting: false
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
  },

  onSlotTab(e) {
    this.setData({ slot: e.currentTarget.dataset.slot })
  },

  onChoosePhoto() {
    if (this.isSlotDone() || this.data.submitting) return
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera', 'album'],
      sizeType: ['compressed'],
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0]
        if (file) {
          this.setData({ photoTemp: file.tempFilePath })
        }
      }
    })
  },

  onRemovePhoto() {
    this.setData({ photoTemp: '' })
  },

  onTextInput(e) {
    this.setData({ text: e.detail.value })
  },

  isSlotDone() {
    return this.data.slot === 'morning' ? this.data.morningDone : this.data.eveningDone
  },

  async onSubmit() {
    const slot = this.data.slot
    if (this.isSlotDone()) {
      wx.showToast({ title: '该时段今天已打卡', icon: 'none' })
      return
    }
    if (this.data.submitting) return

    this.setData({ submitting: true })
    try {
      // 上传照片（允许不带照片，photo 兜底为空）
      let photo = ''
      if (this.data.photoTemp) {
        wx.showLoading({ title: '上传中…' })
        const ext = (this.data.photoTemp.split('.').pop() || 'jpg').toLowerCase()
        const cloudPath = `checkins/${this.planId}/${this.data.today}_${slot}_${Date.now()}.${ext}`
        const up = await wx.cloud.uploadFile({ cloudPath, filePath: this.data.photoTemp })
        photo = up.fileID
        wx.hideLoading()
      }

      const res = await submitCheckin({
        planId: this.planId,
        date: this.data.today,
        slot,
        photo,
        text: this.data.text
      })

      const slotData = { photo, text: this.data.text, time: Date.now(), timeText: formatClock(Date.now()) }
      // 早打完自动切到晚（若晚还没打）
      const nextSlot = slot === 'morning' && !this.data.eveningDone ? 'evening' : slot
      const nextMorningDone = slot === 'morning' ? true : this.data.morningDone
      const nextEveningDone = slot === 'evening' ? true : this.data.eveningDone
      this.setData({
        [slot + 'Done']: true,
        [slot]: slotData,
        slot: nextSlot,
        isDone: nextSlot === 'morning' ? nextMorningDone : nextEveningDone,
        morningDone: nextMorningDone,
        eveningDone: nextEveningDone,
        photoTemp: '',
        text: '',
        submitting: false
      })

      wx.showToast({
        title: slot === 'morning' ? '早打卡成功 🌅' : '晚打卡成功 🌙',
        icon: 'none'
      })
    } catch (e) {
      wx.hideLoading()
      wx.showToast({ title: e.message, icon: 'none' })
      this.setData({ submitting: false })
    }
  },

  onPreview(e) {
    const url = e.currentTarget.dataset.url
    if (url) {
      wx.previewImage({ urls: [url] })
    }
  }
})
