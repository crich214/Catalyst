import { getJournal } from "./api.js";


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown date";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}


function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number(value ?? 0));
}


function formatNumber(value, digits = 1) {
  return Number(value ?? 0).toFixed(digits);
}


function recommendationClass(recommendation = "") {
  switch (String(recommendation).toUpperCase()) {
    case "BUY":
      return "buy";

    case "ACCUMULATE":
      return "accumulate";

    case "SPECULATIVE STARTER":
      return "starter";

    case "WATCH":
      return "watch";

    default:
      return "avoid";
  }
}


function renderReasons(reasons) {
  if (!Array.isArray(reasons) || reasons.length === 0) {
    return "";
  }

  const uniqueReasons = [...new Set(
    reasons
      .filter(Boolean)
      .map((reason) => String(reason).trim())
  )];

  const visibleReasons = uniqueReasons.slice(0, 5);

  return `
    <div class="journal-reasons">
      <h3>Decision Factors</h3>

      <ul class="committee-list">
        ${visibleReasons
          .map(
            (reason) => `
              <li>
                ${escapeHtml(reason)}
              </li>
            `
          )
          .join("")}
      </ul>
    </div>
  `;
}


function renderJournalEntry(entry) {
  const ticker = String(entry.ticker ?? "").toUpperCase();
  const recommendation = String(
    entry.recommendation ?? "WATCH"
  ).toUpperCase();

  return `
    <article
      class="journal-card clickable"
      data-ticker="${escapeHtml(ticker)}"
    >
      <div class="journal-header">
        <div>
          <div class="eyebrow">
            ${formatDate(entry.recorded_at)}
          </div>

          <div class="ticker">
            ${escapeHtml(ticker)}
          </div>

          <div class="company">
            ${escapeHtml(entry.company ?? ticker)}
          </div>
        </div>

        <div>
          <span class="rec ${recommendationClass(recommendation)}">
            ${escapeHtml(recommendation)}
          </span>
        </div>
      </div>

      <div class="portfolio-summary-grid">
        <div class="metric-card">
          <span>Rich Alpha</span>

          <strong>
            ${formatNumber(entry.rich_alpha_score)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Conviction</span>

          <strong>
            ${formatNumber(entry.conviction_score)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Risk</span>

          <strong>
            ${formatNumber(entry.risk_score)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Decision Price</span>

          <strong>
            ${formatCurrency(entry.price)}
          </strong>
        </div>
      </div>

      <div class="journal-body">
        <div class="chairman-message">
          <div class="eyebrow">
            Chairman's Summary
          </div>

          <p>
            ${escapeHtml(
              entry.chairman_summary ??
              "No Chairman summary was recorded."
            )}
          </p>
        </div>

        <div class="journal-action">
          <strong>Committee Action</strong>

          <p>
            ${escapeHtml(
              entry.committee_action ??
              "Not recorded"
            )}
          </p>
        </div>

        ${renderReasons(entry.reasons)}
      </div>
    </article>
  `;
}


function bindJournalClicks(container) {
  container
    .querySelectorAll("[data-ticker]")
    .forEach((entry) => {
      entry.addEventListener("click", (event) => {
        if (event.target.closest("button, a")) {
          return;
        }

        const ticker = entry.dataset.ticker;

        if (
          ticker &&
          typeof window.loadTicker === "function"
        ) {
          window.loadTicker(ticker);
        }
      });
    });
}


export async function loadJournal() {
  const panel = document.getElementById(
    "journalPanel"
  );

  if (!panel) {
    return;
  }

  panel.innerHTML = `
    <div class="loading">
      Loading decision journal...
    </div>
  `;

  try {
    const data = await getJournal(50);

    const entries = Array.isArray(data.entries)
      ? data.entries
      : [];

    if (entries.length === 0) {
      panel.innerHTML = `
        <div class="empty">
          No committee decisions have been recorded yet.
        </div>
      `;

      return;
    }

    panel.innerHTML = `
      <div class="summary-bar">
        <div>
          <strong>${entries.length}</strong>
          Recorded Decisions
        </div>
      </div>

      <div class="journal-timeline">
        ${entries
          .map(renderJournalEntry)
          .join("")}
      </div>
    `;

    bindJournalClicks(panel);
  } catch (error) {
    console.error(
      "Decision journal dashboard error:",
      error
    );

    panel.innerHTML = `
      <div class="error">
        <strong>
          Unable to load the decision journal.
        </strong>

        <div class="small">
          ${escapeHtml(
            error?.message ?? "Unknown error"
          )}
        </div>
      </div>
    `;
  }
}