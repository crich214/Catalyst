import { getEvents } from "./api.js";

export async function loadEvents() {
  const panel = document.getElementById("eventPanel");
  panel.innerHTML = `<div class="loading">Loading Event Intelligence...</div>`;

  try {
    const data = await getEvents();
    const events = data.events || [];

    panel.innerHTML = `
      <table>
        <tr><th>Event</th><th>Score</th><th>Risk</th></tr>
        ${events.slice(0, 8).map(event => `
          <tr>
            <td>
              <div class="ticker">${event.category}</div>
              <div>${event.title}</div>
              <div class="small">${event.summary}</div>
            </td>
            <td><span class="badge">${event.event_score}</span></td>
            <td>${event.risk_level}</td>
          </tr>
        `).join("")}
      </table>
    `;
  } catch {
    panel.innerHTML = `<div class="error">Could not load Event Intelligence.</div>`;
  }
}