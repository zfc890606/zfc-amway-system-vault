// 我的 — 统计
const { stats } = require('../../utils/api')
const { CATEGORIES } = require('../../utils/categories')

Page({
  data: {
    total: 0,
    myCount: 0,
    cats: [],
    loading: true
  },

  onShow() {
    this.load()
  },

  async load() {
    this.setData({ loading: true })
    try {
      const data = await stats()
      const counts = data.counts || {}
      const cats = CATEGORIES.map(c => ({ ...c, count: counts[c.key] || 0 }))
      this.setData({
        total: data.total || 0,
        myCount: data.myCount || 0,
        cats
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ loading: false })
  }
})
