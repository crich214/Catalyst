import { getSignals } from "./api.js";

export async function loadSignals() {
  const panel = document.getElementById("signalPanel");
  panel.innerHTML = `<div class="loading">Loading Signal Engine...</div>`;

  try {
    const data = await getSignals();
    const signals = data.signals || [];

    panel.innerHTML = `
      <table>
        <tr>
          <th>Signal</th>
          <th>Direction</th>
          <th>Weight</th>
        </tr>

        ${signals.slice(0, 8).map(signal => `
          <tr>
            <td>
              <div class="ticker">${signal.type}</div>
              <div>${signal.title}</div>
              <div class="small">${signal.summary}</div>
            </td>

            <td>${signal.direction}</td>

            <td>
              <span class="badge">${signal.weighted_score}</span>
            </td>
          </tr>
        `).join("")}
      </table>
    `;
  } catch {
    panel.innerHTML = `
      <div class="error">
        Could not load Signal Engine.
      </div>
    `;
  }
}