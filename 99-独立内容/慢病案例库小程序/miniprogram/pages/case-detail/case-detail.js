// 案例详情 — 查看 / 编辑 / 删除
const { getCase, updateCase, deleteCase } = require('../../utils/api')
const { CATEGORIES } = require('../../utils/categories')
const { formatTime } = require('../../utils/format')

Page({
  data: {
    id: '',
    caseData: null,
    form: {},
    editing: false,
    color: '#95A5A6',
    updatedAtText: '',
    categories: CATEGORIES.map(c => c.key)
  },

  onLoad(options) {
    this.setData({ id: options.id })
  },

  onShow() {
    this.load()
  },

  async load() {
    try {
      const data = await getCase({ id: this.data.id })
      const colorMap = {}
      CATEGORIES.forEach(c => { colorMap[c.key] = c.color })
      this.setData({
        caseData: data,
        form: { ...data },
        color: colorMap[data.category] || '#95A5A6',
        updatedAtText: formatTime(data.updatedAt)
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
  },

  onEdit() {
    this.setData({ editing: true, form: { ...this.data.caseData } })
  },

  onCancelEdit() {
    this.setData({ editing: false, form: { ...this.data.caseData } })
  },

  onField(e) {
    this.setData({ [`form.${e.currentTarget.dataset.field}`]: e.detail.value })
  },

  onCategory(e) {
    this.setData({ 'form.category': this.data.categories[Number(e.detail.value)] })
  },

  async onSave() {
    const { id, form } = this.data
    const clean = { ...form }
    delete clean._id
    delete clean.openid
    delete clean.deleted
    delete clean.createdAt
    delete clean.updatedAt
    try {
      await updateCase(id, clean)
      wx.showToast({ title: '已更新', icon: 'success' })
      this.load()
      this.setData({ editing: false })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
  },

  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复，确定吗？',
      confirmColor: '#E74C3C',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await deleteCase(this.data.id)
          wx.showToast({ title: '已删除', icon: 'success' })
          setTimeout(() => wx.navigateBack(), 600)
        } catch (e) {
          wx.showToast({ title: e.message, icon: 'none' })
        }
      }
    })
  }
})
