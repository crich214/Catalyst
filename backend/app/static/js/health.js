import { getSystemHealth } from "./api.js";


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function statusClass(status = "") {
  const normalized = String(status).toLowerCase();

  if (
    normalized.includes("live") ||
    normalized.includes("healthy") ||
    normalized.includes("ok")
  ) {
    return "positive";
  }

  if (
    normalized.includes("degraded") ||
    normalized.includes("partial") ||
    normalized.includes("warning")
  ) {
    return "watch";
  }

  return "negative";
}


function scoreClass(score) {
  const numericScore = Number(score ?? 0);

  if (numericScore >= 80) {
    return "positive";
  }

  if (numericScore >= 60) {
    return "watch";
  }

  return "negative";
}


function renderFeed(feed) {
  const name = feed.name ?? "Unknown Feed";
  const status = feed.status ?? "Unknown";
  const score = Number(feed.score ?? 0);
  const detail = feed.detail ?? "";

  return `
    <article class="metric-card health-feed-card">
      <div class="journal-header">
        <div>
          <span>${escapeHtml(name)}</span>

          <strong class="${statusClass(status)}">
            ${escapeHtml(status)}
          </strong>
        </div>

        <div class="health-score ${scoreClass(score)}">
          ${score}
        </div>
      </div>

      <div class="small">
        ${escapeHtml(detail)}
      </div>
    </article>
  `;
}


export async function loadHealth() {
  const healthList = document.getElementById("healthList");
  const overallHealth = document.getElementById("overallHealth");

  if (!healthList) {
    return;
  }

  healthList.innerHTML = `
    <div class="loading">
      Checking system health...
    </div>
  `;

  try {
    const data = await getSystemHealth();

    const feeds = Array.isArray(data.feeds)
      ? data.feeds
      : [];

    const overall = Number(
      data.overall_health ?? 0
    );

    if (overallHealth) {
      overallHealth.innerHTML = `
        System Health
        <strong class="${scoreClass(overall)}">
          ${overall}%
        </strong>
      `;
    }

    healthList.innerHTML = `
      <div class="portfolio-summary-grid">
        ${feeds
          .map(renderFeed)
          .join("")}
      </div>

      ${
        data.next_priority
          ? `
            <div class="chairman-message">
              <div class="eyebrow">
                Next Priority
              </div>

              <p>
                ${escapeHtml(data.next_priority)}
              </p>
            </div>
          `
          : ""
      }
    `;
  } catch (error) {
    console.error(
      "System health dashboard error:",
      error
    );

    if (overallHealth) {
      overallHealth.innerHTML = `
        System Health
        <strong class="negative">
          Offline
        </strong>
      `;
    }

    healthList.innerHTML = `
      <div class="error">
        <strong>
          Unable to load system health.
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