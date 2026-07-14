import { getRadar } from "./api.js";


const ACTIONABLE_RECOMMENDATIONS = new Set([
  "BUY",
  "ACCUMULATE",
  "SPECULATIVE STARTER",
]);


function recommendationClass(recommendation = "") {
  switch (recommendation.toUpperCase()) {
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


function stars(score) {
  const numericScore = Number(score) || 0;

  if (numericScore >= 90) return "★★★★★";
  if (numericScore >= 80) return "★★★★☆";
  if (numericScore >= 70) return "★★★☆☆";
  if (numericScore >= 60) return "★★☆☆☆";

  return "★☆☆☆☆";
}


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function normalizeRow(row) {
  if (!row || typeof row !== "object") {
    return null;
  }

  const ticker = String(row.ticker ?? "").trim().toUpperCase();

  if (!ticker) {
    return null;
  }

  const score = Number(
    row.adjusted_rich_alpha_score ??
    row.rich_alpha_score ??
    0
  );

  const recommendation = String(
    row.recommendation ?? "WATCH"
  ).toUpperCase();

  return {
    ...row,
    ticker,
    company: row.company ?? ticker,
    category: row.category ?? "",
    recommendation,
    score,
    riskScore: row.risk_score ?? "--",
    marginOfSafety:
      row.accumulation_plan?.estimated_margin_of_safety_pct ?? null,
  };
}


function renderSummary(summaryElement, actionable, opportunities, stats) {
  if (!summaryElement) {
    return;
  }

  summaryElement.innerHTML = `
    <div class="summary-bar">
      <div>
        <strong>${actionable.length}</strong>
        Actionable
      </div>

      <div>
        <strong>${opportunities.length}</strong>
        Companies
      </div>

      <div>
        <strong>${Number(stats.live ?? 0)}</strong>
        Live
      </div>

      <div>
        <strong>${Number(stats.partial_live ?? 0)}</strong>
        Partial Live
      </div>
    </div>
  `;
}


function renderActionableCard(row) {
  const marginSafety = row.marginOfSafety === null
    ? "--"
    : `${row.marginOfSafety}%`;

  return `
    <article
      class="opportunity-card clickable"
      role="button"
      tabindex="0"
      data-ticker="${escapeHtml(row.ticker)}"
    >
      <div class="opportunity-header">
        <div>
          <div class="stars">
            ${stars(row.score)}
          </div>

          <div class="ticker">
            ${escapeHtml(row.ticker)}
          </div>

          <div class="company">
            ${escapeHtml(row.company)}
          </div>

          ${
            row.category
              ? `
                <div class="small">
                  ${escapeHtml(row.category)}
                </div>
              `
              : ""
          }
        </div>

        <div class="rec ${recommendationClass(row.recommendation)}">
          ${escapeHtml(row.recommendation)}
        </div>
      </div>

      <div class="metrics">
        <div>
          <span>Rich Alpha</span>
          <strong>${row.score.toFixed(1)}</strong>
        </div>

        <div>
          <span>Margin Safety</span>
          <strong>${marginSafety}</strong>
        </div>

        <div>
          <span>Risk</span>
          <strong>${escapeHtml(row.riskScore)}</strong>
        </div>
      </div>
    </article>
  `;
}


function renderWatchRow(row) {
  return `
    <tr
      class="clickable"
      data-ticker="${escapeHtml(row.ticker)}"
    >
      <td>
        <strong>${escapeHtml(row.ticker)}</strong>
      </td>

      <td>
        <div>${escapeHtml(row.company)}</div>
        ${
          row.category
            ? `<div class="small">${escapeHtml(row.category)}</div>`
            : ""
        }
      </td>

      <td>${row.score.toFixed(1)}</td>

      <td>
        <span class="rec ${recommendationClass(row.recommendation)}">
          ${escapeHtml(row.recommendation)}
        </span>
      </td>
    </tr>
  `;
}


function bindTickerClicks(container) {
  container
    .querySelectorAll("[data-ticker]")
    .forEach((element) => {
      const openTicker = () => {
        const ticker = element.dataset.ticker;

        if (ticker && typeof window.loadTicker === "function") {
          window.loadTicker(ticker);
        }
      };

      element.addEventListener("click", openTicker);

      element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openTicker();
        }
      });
    });
}


export async function loadRadar() {
  const radar = document.getElementById("radar");
  const summary = document.getElementById("opportunitySummary");

  if (!radar) {
    console.error("Catalyst radar container was not found.");
    return;
  }

  radar.innerHTML = `
    <div class="loading">
      Scanning live opportunities...
    </div>
  `;

  try {
    const data = await getRadar();

    if (!data || typeof data !== "object") {
      throw new Error("Opportunity API returned an invalid response.");
    }

    const opportunities = (
      Array.isArray(data.ranked_opportunities)
        ? data.ranked_opportunities
        : []
    )
      .map(normalizeRow)
      .filter(Boolean);

    const suppliedActionable = Array.isArray(
      data.actionable_opportunities
    )
      ? data.actionable_opportunities
          .map(normalizeRow)
          .filter(Boolean)
      : [];

    const actionable = suppliedActionable.length
      ? suppliedActionable
      : opportunities.filter((row) =>
          ACTIONABLE_RECOMMENDATIONS.has(row.recommendation)
        );

    const watchlist = opportunities
      .filter(
        (row) =>
          !ACTIONABLE_RECOMMENDATIONS.has(row.recommendation)
      )
      .slice(0, 12);

    renderSummary(
      summary,
      actionable,
      opportunities,
      data.summary ?? {}
    );

    const actionableHtml = actionable.length
      ? actionable.map(renderActionableCard).join("")
      : `
          <div class="empty">
            No actionable opportunities currently meet Catalyst criteria.
          </div>
        `;

    const watchlistHtml = watchlist.length
      ? watchlist.map(renderWatchRow).join("")
      : `
          <tr>
            <td colspan="4">
              No watchlist companies are currently available.
            </td>
          </tr>
        `;

    radar.innerHTML = `
      <div class="radar-section">
        <h3>Actionable Opportunities</h3>

        <div class="opportunity-grid">
          ${actionableHtml}
        </div>
      </div>

      <div class="radar-section">
        <h3>Watchlist</h3>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company</th>
                <th>Score</th>
                <th>Recommendation</th>
              </tr>
            </thead>

            <tbody>
              ${watchlistHtml}
            </tbody>
          </table>
        </div>
      </div>
    `;

    bindTickerClicks(radar);
  } catch (error) {
    console.error("Opportunity Board error:", error);

    radar.innerHTML = `
      <div class="error">
        <strong>Opportunity Board unavailable.</strong>
        <div class="small">
          ${escapeHtml(error?.message ?? "Unknown rendering error")}
        </div>
      </div>
    `;
  }
}