import { getSignals } from "./api.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function directionClass(direction) {
  const value = String(direction ?? "").toLowerCase();

  if (value.includes("bull")) return "buy";
  if (value.includes("bear")) return "avoid";

  return "watch";
}

export async function loadSignals() {

  const panel = document.getElementById("signalPanel");

  if (!panel) return;

  panel.innerHTML = `
    <div class="loading">
      Building Signal Engine...
    </div>
  `;

  try {

    const data = await getSignals();

    const signals = data.signals || [];

    if (!signals.length) {

      panel.innerHTML = `
        <div class="empty">
          No active signals.
        </div>
      `;

      return;
    }

    panel.innerHTML = signals
      .slice(0, 10)
      .map(signal => `

        <article class="journal-card">

          <div class="journal-header">

            <div>

              <div class="eyebrow">

                ${escapeHtml(signal.factor ?? signal.category)}

              </div>

              <strong>

                ${escapeHtml(signal.title)}

              </strong>

              <div class="small">

                ${escapeHtml(signal.source)}

              </div>

            </div>

            <div>

              <span class="rec ${directionClass(signal.direction)}">

                ${escapeHtml(signal.direction)}

              </span>

            </div>

          </div>

          <div class="journal-body">

            <p>

              ${escapeHtml(signal.summary)}

            </p>

            <div class="portfolio-summary-grid">

              <div class="metric-card">

                <span>Weighted Score</span>

                <strong>

                  ${Number(signal.weighted_score ?? 0)}

                </strong>

              </div>

              <div class="metric-card">

                <span>Confidence</span>

                <strong>

                  ${Number(signal.confidence ?? 0)}%

                </strong>

              </div>

              <div class="metric-card">

                <span>Materiality</span>

                <strong>

                  ${escapeHtml(signal.materiality ?? "Medium")}

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
        Unable to load Signal Engine.
      </div>
    `;

  }

}