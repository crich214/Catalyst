import { getMarketRegime } from "./api.js";

export async function loadRegime() {
  try {
    const data = await getMarketRegime();

    document.getElementById("regimeTitle").textContent = data.regime;
    document.getElementById("regimeSummary").textContent = data.summary;
    document.getElementById("regimeScore").textContent = data.regime_score;

    document.getElementById("favoredThemes").innerHTML =
      (data.favored_themes || []).map(t => `<div class="chip">${t}</div>`).join("");

    const macro = data.data || {};
    const rows = [
      ["Fed Funds", macro.fed_funds],
      ["10Y Treasury", macro.ten_year],
      ["2Y Treasury", macro.two_year],
      ["Unemployment", macro.unemployment],
      ["Credit Spread", macro.credit_spread],
      ["VIX", macro.vix],
    ];

    document.getElementById("macroFacts").innerHTML = `
      <table>
        <tr><th>Macro Signal</th><th>Latest</th><th>Date</th><th>Status</th></tr>
        ${rows.map(([label, item]) => `
          <tr>
            <td>${label}</td>
            <td>${item && item.value !== null ? Number(item.value).toFixed(2) + " " + (item.unit || "") : "N/A"}</td>
            <td>${item ? item.date : "N/A"}</td>
            <td>${item ? item.status : "N/A"}</td>
          </tr>
        `).join("")}
      </table>
    `;
  } catch {
    document.getElementById("regimeTitle").textContent = "Unavailable";
  }
}