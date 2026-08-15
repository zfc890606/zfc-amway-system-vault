// 首页 — 案例库列表
const { listCases } = require('../../utils/api')
const { CATEGORIES } = require('../../utils/categories')
const { formatTime } = require('../../utils/format')

Page({
  data: {
    categories: CATEGORIES,
    activeTab: '',
    keyword: '',
    cases: [],
    loading: true
  },

  onShow() {
    this.load()
  },

  onPullDownRefresh() {
    this.load().finally(() => wx.stopPullDownRefresh())
  },

  onSearchInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  onClearSearch() {
    this.setData({ keyword: '' })
    this.load()
  },

  onTab(e) {
    this.setData({ activeTab: e.currentTarget.dataset.key || '' })
    this.load()
  },

  async load() {
    this.setData({ loading: true })
    try {
      const data = await listCases({
        category: this.data.activeTab || '',
        keyword: this.data.keyword || ''
      })
      const colorMap = {}
      CATEGORIES.forEach(c => { colorMap[c.key] = c.color })
      const cases = (data || []).map(c => ({
        ...c,
        tags: c.tags || [],
        color: colorMap[c.category] || '#95A5A6',
        updatedAtText: formatTime(c.updatedAt)
      }))
      this.setData({ cases })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ loading: false })
  },

  onOpen(e) {
    wx.navigateTo({ url: '/pages/case-detail/case-detail?id=' + e.currentTarget.dataset.id })
  }
})
