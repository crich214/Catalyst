import { getRadar } from "./api.js";

export async function loadRadar() {
  const radar = document.getElementById("radar");
  radar.innerHTML = `<div class="loading">Loading Opportunity Radar...</div>`;

  try {
    const data = await getRadar();
    const rows = data.ranked_opportunities || [];

    radar.innerHTML = `
      <table>
        <tr><th>Rank</th><th>Company</th><th>Score</th><th>Committee</th><th>Action</th></tr>
        ${rows.slice(0, 20).map((row, i) => `
          <tr class="clickable" onclick="window.loadTicker('${row.ticker}')">
            <td>${i + 1}</td>
            <td>
              <div class="ticker">${row.ticker}</div>
              <div>${row.company}</div>
              <div class="small">${row.category}</div>
            </td>
            <td><span class="badge">${row.adjusted_rich_alpha_score ?? row.rich_alpha_score}</span></td>
            <td>${row.signal_adjustment ? `Signal ${row.signal_adjustment}` : "No material change"}</td>
            <td><span class="rec">${row.recommendation}</span></td>
          </tr>
        `).join("")}
      </table>
    `;
  } catch {
    radar.innerHTML = `<div class="error">Could not load Opportunity Radar.</div>`;
  }
}