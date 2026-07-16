import { getMarketRegime } from "./api.js";


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function formatNumber(value, digits = 2) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  return number.toFixed(digits);
}


function renderThemes(themes) {
  if (!Array.isArray(themes) || themes.length === 0) {
    return `
      <div class="small">
        No favored themes are currently available.
      </div>
    `;
  }

  return themes
    .map(
      (theme) => `
        <span class="chip">
          ${escapeHtml(theme)}
        </span>
      `
    )
    .join("");
}


function renderMacroFacts(data) {
  const facts = [
    {
      label: "Risk Level",
      value: data.risk_level ?? "Unknown",
    },
    {
      label: "Fed Funds",
      value:
        data.fed_funds_rate != null
          ? `${formatNumber(data.fed_funds_rate)}%`
          : "--",
    },
    {
      label: "10Y Treasury",
      value:
        data.ten_year_yield != null
          ? `${formatNumber(data.ten_year_yield)}%`
          : "--",
    },
    {
      label: "2Y Treasury",
      value:
        data.two_year_yield != null
          ? `${formatNumber(data.two_year_yield)}%`
          : "--",
    },
    {
      label: "Yield Curve",
      value:
        data.yield_curve != null
          ? formatNumber(data.yield_curve)
          : "--",
    },
    {
      label: "Unemployment",
      value:
        data.unemployment_rate != null
          ? `${formatNumber(data.unemployment_rate)}%`
          : "--",
    },
  ];

  return `
    <div class="portfolio-summary-grid">
      ${facts
        .map(
          (fact) => `
            <div class="metric-card">
              <span>${escapeHtml(fact.label)}</span>
              <strong>${escapeHtml(fact.value)}</strong>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}


export async function loadRegime() {
  const scoreElement = document.getElementById("regimeScore");
  const titleElement = document.getElementById("regimeTitle");
  const summaryElement = document.getElementById("regimeSummary");
  const themesElement = document.getElementById("favoredThemes");
  const factsElement = document.getElementById("macroFacts");

  if (
    !scoreElement ||
    !titleElement ||
    !summaryElement ||
    !themesElement ||
    !factsElement
  ) {
    return;
  }

  titleElement.textContent = "Loading...";
  summaryElement.textContent = "Retrieving current macro conditions.";
  themesElement.innerHTML = "";
  factsElement.innerHTML = "";

  try {
    const data = await getMarketRegime();

    const score = Number(
      data.regime_score ??
      data.macro_score ??
      data.score ??
      50
    );

    const regime =
      data.regime ??
      data.market_regime ??
      data.title ??
      "Unknown";

    const summary =
      data.summary ??
      data.portfolio_bias ??
      "No macro summary is currently available.";

    const favoredThemes =
      data.favored_themes ??
      data.favoredThemes ??
      [];

    scoreElement.textContent = formatNumber(score, 0);
    titleElement.textContent = regime;
    summaryElement.textContent = summary;
    themesElement.innerHTML = renderThemes(favoredThemes);
    factsElement.innerHTML = renderMacroFacts(data);
  } catch (error) {
    console.error(
      "Market regime dashboard error:",
      error
    );

    scoreElement.textContent = "--";
    titleElement.textContent = "Unavailable";

    summaryElement.innerHTML = `
      <div class="error">
        <strong>
          Unable to load the current market regime.
        </strong>

        <div class="small">
          ${escapeHtml(
            error?.message ?? "Unknown error"
          )}
        </div>
      </div>
    `;

    themesElement.innerHTML = "";
    factsElement.innerHTML = "";
  }
}