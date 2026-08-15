// 新增案例 — 表单 + AI 智能归类
const { classifyCase, addCase } = require('../../utils/api')
const { CATEGORIES } = require('../../utils/categories')

Page({
  data: {
    categories: CATEGORIES.map(c => c.key),
    colorMap: (() => {
      const m = {}
      CATEGORIES.forEach(c => { m[c.key] = c.color })
      return m
    })(),
    rawText: '',
    aiLoading: false,
    saving: false,
    aiResult: null,
    aiColor: '#95A5A6',
    form: {
      title: '',
      category: '',
      alias: '',
      ageRange: '',
      chiefComplaint: '',
      metrics: '',
      plan: '',
      result: ''
    }
  },

  onRawInput(e) {
    this.setData({ rawText: e.detail.value })
  },

  onField(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },

  onCategory(e) {
    const idx = Number(e.detail.value)
    this.setData({ 'form.category': this.data.categories[idx] })
  },

  async onAiClassify() {
    const text = this.data.rawText.trim()
    if (text.length < 10) {
      wx.showToast({ title: '请先粘贴案例内容（至少10字）', icon: 'none' })
      return
    }
    this.setData({ aiLoading: true })
    try {
      const ai = await classifyCase({ text })
      const form = { ...this.data.form }
      if (ai.title) form.title = ai.title
      if (ai.category) form.category = ai.category
      if (ai.ageRange) form.ageRange = ai.ageRange
      if (ai.alias) form.alias = ai.alias
      if (ai.chiefComplaint) form.chiefComplaint = ai.chiefComplaint
      if (ai.metricsText) form.metrics = ai.metricsText
      this.setData({
        aiResult: {
          category: ai.category || '其他',
          title: ai.title || '',
          tags: ai.tags || []
        },
        aiColor: this.data.colorMap[ai.category] || '#95A5A6',
        form
      })
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ aiLoading: false })
  },

  async onSave() {
    const { form } = this.data
    if (!form.title.trim()) {
      wx.showToast({ title: '请填写标题', icon: 'none' })
      return
    }
    if (!form.category) {
      wx.showToast({ title: '请选择板块', icon: 'none' })
      return
    }
    this.setData({ saving: true })
    try {
      await addCase({ payload: form })
      wx.showToast({ title: '已入库', icon: 'success' })
      setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 600)
    } catch (e) {
      wx.showToast({ title: e.message, icon: 'none' })
    }
    this.setData({ saving: false })
  }
})
