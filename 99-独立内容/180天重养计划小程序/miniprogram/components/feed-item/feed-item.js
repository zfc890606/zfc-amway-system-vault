// 组件：feed-item — 今日动态单条
const { formatClock } = require('../../utils/format')

Component({
  properties: {
    item: { type: Object, value: null }
  },

  data: {
    vm: null
  },

  observers: {
    item(item) {
      if (!item) {
        this.setData({ vm: null })
        return
      }
      const morning = item.morning ? { ...item.morning, timeText: formatClock(item.morning.time) } : null
      const evening = item.evening ? { ...item.evening, timeText: formatClock(item.evening.time) } : null
      this.setData({
        vm: {
          ...item,
          morning,
          evening,
          initial: (item.nickname || '友')[0],
          morningHasPhoto: !!(morning && morning.photo),
          eveningHasPhoto: !!(evening && evening.photo)
        }
      })
    }
  },

  methods: {
    onPreview(e) {
      const url = e.currentTarget.dataset.url
      if (url) {
        wx.previewImage({ urls: [url] })
      }
    }
  }
})
