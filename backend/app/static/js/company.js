import {
  getCommittee,
  getCompany,
  recordJournalDecision,
} from "./api.js";


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function formatCurrency(value) {
  const number = Number(value ?? 0);

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(number);
}


function formatNumber(value, digits = 1) {
  return Number(value ?? 0).toFixed(digits);
}


function formatPercent(value) {
  const number = Number(value ?? 0);
  const sign = number > 0 ? "+" : "";

  return `${sign}${number.toFixed(1)}%`;
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


function stanceClass(stance = "") {
  const normalized = String(stance).toLowerCase();

  if (
    normalized.includes("support") ||
    normalized.includes("constructive") ||
    normalized.includes("positive")
  ) {
    return "positive";
  }

  if (
    normalized.includes("restrictive") ||
    normalized.includes("cautious") ||
    normalized.includes("negative")
  ) {
    return "negative";
  }

  return "neutral";
}


function scoreLabel(score) {
  const numericScore = Number(score ?? 0);

  if (numericScore >= 85) {
    return "Exceptional";
  }

  if (numericScore >= 75) {
    return "Strong";
  }

  if (numericScore >= 65) {
    return "Constructive";
  }

  if (numericScore >= 55) {
    return "Mixed";
  }

  return "Weak";
}


function renderScoreCard(label, value, suffix = "") {
  const numericValue = Number(value ?? 0);

  return `
    <div class="metric-card">
      <span>${escapeHtml(label)}</span>

      <strong>
        ${formatNumber(numericValue, 1)}${suffix}
      </strong>

      <div class="small">
        ${scoreLabel(numericValue)}
      </div>
    </div>
  `;
}


function renderList(items, emptyText) {
  if (!Array.isArray(items) || items.length === 0) {
    return `
      <div class="small">
        ${escapeHtml(emptyText)}
      </div>
    `;
  }

  return `
    <ul class="committee-list">
      ${items
        .map(
          (item) => `
            <li>
              ${escapeHtml(item)}
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}


function renderAnalystReview(review) {
  const stance = review.stance ?? review.assessment ?? "Neutral";
  const confidence = Number(review.confidence ?? 0);

  return `
    <article class="journal-card committee-member-card">
      <div class="journal-header">
        <div>
          <div class="eyebrow">
            ${escapeHtml(review.domain ?? "Committee")}
          </div>

          <div class="ticker">
            ${escapeHtml(review.member ?? "Analyst")}
          </div>

          <div class="small">
            ${escapeHtml(review.role ?? "")}
          </div>
        </div>

        <div>
          <span class="rec ${stanceClass(stance)}">
            ${escapeHtml(stance)}
          </span>
        </div>
      </div>

      <div class="portfolio-summary-grid committee-review-metrics">
        <div class="metric-card">
          <span>Assessment</span>
          <strong>${escapeHtml(review.assessment ?? "Not available")}</strong>
        </div>

        <div class="metric-card">
          <span>Confidence</span>
          <strong>${formatNumber(confidence, 0)}</strong>
        </div>
      </div>

      <div class="journal-body">
        <p>
          ${escapeHtml(review.summary ?? "")}
        </p>

        <div class="committee-review-grid">
          <div>
            <h3>Positives</h3>
            ${renderList(
              review.positives,
              "No specific positives recorded."
            )}
          </div>

          <div>
            <h3>Concerns</h3>
            ${renderList(
              review.concerns,
              "No material concerns recorded."
            )}
          </div>
        </div>
      </div>
    </article>
  `;
}


function renderAccumulationPlan(plan) {
  if (!plan || typeof plan !== "object") {
    return "";
  }

  const ladder = Array.isArray(plan.ladder)
    ? plan.ladder
    : [];

  const ladderRows = ladder.length
    ? ladder
        .map(
          (item) => `
            <tr>
              <td>${escapeHtml(item.price_zone)}</td>
              <td>${escapeHtml(item.action)}</td>
              <td>${escapeHtml(item.target_position)}</td>
            </tr>
          `
        )
        .join("")
    : `
        <tr>
          <td colspan="3">
            No accumulation ladder is available.
          </td>
        </tr>
      `;

  return `
    <div class="performance-comparison">
      <h3>Accumulation Plan</h3>

      <div class="portfolio-summary-grid">
        <div class="metric-card">
          <span>Strategy</span>
          <strong>${escapeHtml(plan.strategy ?? "Watch")}</strong>
        </div>

        <div class="metric-card">
          <span>Margin of Safety</span>
          <strong>
            ${formatPercent(
              plan.estimated_margin_of_safety_pct ?? 0
            )}
          </strong>
        </div>

        <div class="metric-card">
          <span>Maximum Position</span>
          <strong>${escapeHtml(plan.max_position ?? "--")}</strong>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Price Zone</th>
              <th>Action</th>
              <th>Target Position</th>
            </tr>
          </thead>

          <tbody>
            ${ladderRows}
          </tbody>
        </table>
      </div>
    </div>
  `;
}


function renderInformationEvents(briefing) {
  const items = Array.isArray(briefing?.items)
    ? briefing.items
    : [];

  if (items.length === 0) {
    return "";
  }

  return `
    <div class="performance-comparison">
      <h3>Material Investment Events</h3>

      <div class="committee-events">
        ${items
          .slice(0, 6)
          .map(
            (item) => `
              <article class="journal-card">
                <div class="journal-header">
                  <div>
                    <div class="eyebrow">
                      ${escapeHtml(item.event_type ?? item.category ?? "Event")}
                    </div>

                    <strong>
                      ${escapeHtml(item.title ?? "Untitled")}
                    </strong>

                    <div class="small">
                      ${escapeHtml(item.source ?? "Unknown source")}
                    </div>
                  </div>

                  <span class="rec ${recommendationClass(
                    item.direction === "Bullish"
                      ? "ACCUMULATE"
                      : item.direction === "Bearish"
                        ? "AVOID"
                        : "WATCH"
                  )}">
                    ${escapeHtml(item.materiality ?? "Low")}
                  </span>
                </div>

                <div class="journal-body">
                  <p>
                    ${escapeHtml(item.summary ?? "")}
                  </p>
                </div>
              </article>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}


async function saveDecision(ticker, button) {
  const originalText = button.textContent;

  button.disabled = true;
  button.textContent = "Recording...";

  try {
    await recordJournalDecision(ticker);
    button.textContent = "Decision Recorded";
  } catch (error) {
    console.error("Journal recording error:", error);
    button.textContent = "Record Failed";
  } finally {
    window.setTimeout(() => {
      button.disabled = false;
      button.textContent = originalText;
    }, 1800);
  }
}


function bindCommitteeActions(container, ticker) {
  const recordButton = container.querySelector(
    "[data-record-decision]"
  );

  if (recordButton) {
    recordButton.addEventListener("click", () => {
      saveDecision(ticker, recordButton);
    });
  }
}


function getRequestedTicker(explicitTicker) {
  if (explicitTicker) {
    return String(explicitTicker)
      .trim()
      .toUpperCase();
  }

  const input = document.getElementById("tickerInput");

  return String(input?.value ?? "")
    .trim()
    .toUpperCase();
}


export async function loadTicker(explicitTicker = "") {
  const resultCard = document.getElementById("resultCard");
  const tickerInput = document.getElementById("tickerInput");

  if (!resultCard) {
    return;
  }

  const ticker = getRequestedTicker(explicitTicker);

  if (!ticker) {
    resultCard.innerHTML = `
      <div class="error">
        Enter a ticker to convene the committee.
      </div>
    `;

    return;
  }

  if (tickerInput) {
    tickerInput.value = ticker;
  }

  resultCard.innerHTML = `
    <div class="loading">
      Convening the Catalyst Investment Committee for
      ${escapeHtml(ticker)}...
    </div>
  `;

  try {
    const [
      companyResult,
      committeeResult,
    ] = await Promise.all([
      getCompany(ticker),
      getCommittee(ticker),
    ]);

    const company = companyResult.data ?? {};
    const committeePayload = committeeResult.data ?? {};

    const decision = committeePayload.decision ?? {};
    const profile =
      committeePayload.company_profile ??
      company ??
      {};
    const briefing =
      committeePayload.information_briefing ??
      {};

    const recommendation =
      decision.final_recommendation ??
      decision.decision_engine_recommendation ??
      profile.recommendation ??
      "WATCH";

    const committeeAction =
      decision.committee_action ??
      "REVIEW";

    const analystReviews = Array.isArray(
      decision.analyst_reviews
    )
      ? decision.analyst_reviews
      : [];

    const adjustedScore = Number(
      profile.adjusted_rich_alpha_score ??
      profile.rich_alpha_score ??
      decision.decision_engine_score ??
      0
    );

    const conviction = Number(
      decision.conviction ??
      profile.conviction_score ??
      0
    );

    const riskScore = Number(
      profile.risk_score ?? 0
    );

    const marginOfSafety = Number(
      profile.accumulation_plan
        ?.estimated_margin_of_safety_pct ?? 0
    );

    resultCard.innerHTML = `
      <section class="committee-dashboard">
        <div class="opportunity-header committee-hero">
          <div>
            <div class="eyebrow">
              Catalyst Investment Committee
            </div>

            <div class="ticker">
              ${escapeHtml(profile.ticker ?? ticker)}
            </div>

            <div class="company">
              ${escapeHtml(profile.company ?? ticker)}
            </div>

            <div class="small">
              ${escapeHtml(profile.category ?? "")}
            </div>
          </div>

          <div class="committee-decision-block">
            <span class="rec ${recommendationClass(recommendation)}">
              ${escapeHtml(recommendation)}
            </span>

            <div class="small">
              Committee Action:
              ${escapeHtml(committeeAction)}
            </div>
          </div>
        </div>

        <div class="portfolio-summary-grid">
          ${renderScoreCard(
            "Rich Alpha",
            adjustedScore
          )}

          ${renderScoreCard(
            "Conviction",
            conviction
          )}

          ${renderScoreCard(
            "Risk",
            riskScore
          )}

          <div class="metric-card">
            <span>Margin of Safety</span>

            <strong>
              ${formatPercent(marginOfSafety)}
            </strong>

            <div class="small">
              Current price:
              ${formatCurrency(profile.price)}
            </div>
          </div>
        </div>

        <div class="chairman-message">
          <div class="eyebrow">
            Chairman's Recommendation
          </div>

          <h3>
            ${escapeHtml(recommendation)}
          </h3>

          <p>
            ${escapeHtml(
              decision.chairman_summary ??
              profile.top_reason ??
              "No Chairman summary is currently available."
            )}
          </p>

          <button
            class="secondary"
            data-record-decision
          >
            Record Decision
          </button>
        </div>

        <div class="committee-members">
          ${analystReviews
            .map(renderAnalystReview)
            .join("")}
        </div>

        ${renderAccumulationPlan(
          profile.accumulation_plan
        )}

        ${renderInformationEvents(briefing)}
      </section>
    `;

    bindCommitteeActions(resultCard, ticker);
  } catch (error) {
    console.error(
      "Committee dashboard error:",
      error
    );

    resultCard.innerHTML = `
      <div class="error">
        <strong>
          Unable to convene the committee for
          ${escapeHtml(ticker)}.
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