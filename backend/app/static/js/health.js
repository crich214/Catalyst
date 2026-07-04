import { getSystemHealth } from "./api.js";

export async function loadHealth() {
  const list = document.getElementById("healthList");
  list.innerHTML = `<div class="loading">Checking system health...</div>`;

  try {
    const data = await getSystemHealth();

    document.getElementById("overallHealth").innerHTML =
      `System Health <strong>${data.overall_health}%</strong>`;

    list.innerHTML = (data.feeds || []).map(feed => `
      <div class="reason">
        <strong>${feed.name}</strong> — ${feed.status}<br>
        <span class="small">${feed.detail}</span>
      </div>
    `).join("");
  } catch {
    list.innerHTML = `<div class="error">System health unavailable.</div>`;
  }
}