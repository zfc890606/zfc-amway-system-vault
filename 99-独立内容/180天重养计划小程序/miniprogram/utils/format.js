// 格式化工具
function pad(n) {
  return n < 10 ? '0' + n : '' + n
}

// 时间戳 → YYYY-MM-DD
function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  const y = d.getFullYear()
  const m = pad(d.getMonth() + 1)
  const day = pad(d.getDate())
  return `${y}-${m}-${day}`
}

// 时间戳 → HH:mm
function formatClock(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

module.exports = { formatTime, formatClock }
