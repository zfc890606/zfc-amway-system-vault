// 组件：calendar — 180格打卡日历（6阶段 × 30天，GitHub风紧凑格子）
const { PHASES } = require('../../utils/content')

function cellColor(status) {
  if (status >= 3) return '#2E9E6B' // 早晚都完成
  if (status === 2) return '#7FCFA8' // 仅晚
  if (status === 1) return '#B5E2C7' // 仅早
  return '#EDF2ED' // 未打卡
}

Component({
  properties: {
    dayStatus: { type: Array, value: [] },
    todayIdx: { type: Number, value: -1 }
  },

  data: {
    rows: []
  },

  observers: {
    'dayStatus, todayIdx': function (dayStatus, todayIdx) {
      const status = Array.isArray(dayStatus) && dayStatus.length === 180
        ? dayStatus
        : new Array(180).fill(0)
      const rows = PHASES.map(p => {
        const start = (p.phase - 1) * 30
        const cells = []
        for (let i = 0; i < 30; i++) {
          const idx = start + i
          const s = status[idx] || 0
          cells.push({
            dayNo: idx + 1,
            status: s,
            color: cellColor(s),
            isToday: idx === todayIdx
          })
        }
        return { ...p, cells }
      })
      this.setData({ rows })
    }
  }
})
