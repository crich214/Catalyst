export function fmtMoney(value) {
  if (value === null || value === undefined) return "N/A";
  if (Math.abs(value) >= 1_000_000_000_000) return "$" + (value / 1_000_000_000_000).toFixed(2) + "T";
  if (Math.abs(value) >= 1_000_000_000) return "$" + (value / 1_000_000_000).toFixed(2) + "B";
  if (Math.abs(value) >= 1_000_000) return "$" + (value / 1_000_000).toFixed(2) + "M";
  return "$" + Number(value).toFixed(2);
}

export function safeNumber(value, decimals = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "N/A";
  return Number(value).toFixed(decimals);
}