// 日期工具 — 全部用 Date.UTC 求差值，避免时区坑
function pad(n) {
  return n < 10 ? '0' + n : '' + n
}

// 本地日期 YYYY-MM-DD（客户端打卡按本地日期分桶）
function getToday() {
  const d = new Date()
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// 日期加 n 天，返回 YYYY-MM-DD（n 可为负）
function addDays(dateStr, n) {
  const [y, m, d] = dateStr.split('-').map(Number)
  const dt = new Date(Date.UTC(y, m - 1, d))
  dt.setUTCDate(dt.getUTCDate() + n)
  return `${dt.getUTCFullYear()}-${pad(dt.getUTCMonth() + 1)}-${pad(dt.getUTCDate())}`
}

// 把 YYYY-MM-DD 转成 UTC 天数
function utcDay(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number)
  return Date.UTC(y, m - 1, d) / 86400000
}

// b - a 的天数差
function dayDiff(a, b) {
  return utcDay(b) - utcDay(a)
}

// 计划第几天：startDate 当天 = 第1天
function dayNo(startDate, dateStr) {
  return dayDiff(startDate, dateStr) + 1
}

module.exports = { getToday, addDays, utcDay, dayDiff, dayNo }
