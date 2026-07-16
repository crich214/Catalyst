import { getEvents } from "./api.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function eventClass(direction) {
  const value = String(direction ?? "").toLowerCase();

  if (value.includes("bull")) {
    return "buy";
  }

  if (value.includes("bear")) {
    return "avoid";
  }

  return "watch";
}

function materialityClass(materiality) {
  const value = String(materiality ?? "").toLowerCase();

  if (value.includes("high")) {
    return "buy";
  }

  if (value.includes("medium")) {
    return "watch";
  }

  return "neutral";
}

export async function loadEvents() {

  const panel = document.getElementById("eventPanel");

  if (!panel) return;

  panel.innerHTML = `
    <div class="loading">
      Loading Event Intelligence...
    </div>
  `;

  try {

    const data = await getEvents();

    const events = data.events || [];

    if (events.length === 0) {

      panel.innerHTML = `
        <div class="empty">
          No material investment events.
        </div>
      `;

      return;
    }

    panel.innerHTML = events
      .slice(0, 10)
      .map(event => `

        <article class="journal-card">

          <div class="journal-header">

            <div>

              <div class="eyebrow">

                ${escapeHtml(event.category)}

              </div>

              <strong>

                ${escapeHtml(event.title)}

              </strong>

              <div class="small">

                ${escapeHtml(event.source)}

              </div>

            </div>

            <div>

              <span class="rec ${materialityClass(event.materiality)}">

                ${escapeHtml(event.materiality)}

              </span>

            </div>

          </div>

          <div class="journal-body">

            <p>

              ${escapeHtml(event.summary)}

            </p>

            <div class="portfolio-summary-grid">

              <div class="metric-card">

                <span>Direction</span>

                <strong class="${eventClass(event.direction)}">

                  ${escapeHtml(event.direction)}

                </strong>

              </div>

              <div class="metric-card">

                <span>Confidence</span>

                <strong>

                  ${Number(event.confidence ?? 0)}%

                </strong>

              </div>

              <div class="metric-card">

                <span>Event Type</span>

                <strong>

                  ${escapeHtml(event.event_type)}

                </strong>

              </div>

            </div>

          </div>

        </article>

      `)
      .join("");

  }

  catch (err) {

    console.error(err);

    panel.innerHTML = `
      <div class="error">

        Unable to load Event Intelligence.

      </div>
    `;

  }

}