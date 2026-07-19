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
  const macro = data.data || {};

  const facts = [
    {
      label: "Risk Level",
      value: data.risk_level ?? "Unknown",
    },
    {
      label: "Fed Funds",
      value:
        macro.fed_funds?.value != null
          ? `${formatNumber(macro.fed_funds.value)}%`
          : "--",
    },
    {
      label: "10Y Treasury",
      value:
        macro.ten_year?.value != null
          ? `${formatNumber(macro.ten_year.value)}%`
          : "--",
    },
    {
      label: "2Y Treasury",
      value:
        macro.two_year?.value != null
          ? `${formatNumber(macro.two_year.value)}%`
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
        macro.unemployment?.value != null
          ? `${formatNumber(macro.unemployment.value)}%`
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

    const portfolioBias = data.portfolio_bias;

    const summary =
      data.summary ??
      (
        typeof portfolioBias === "string"
          ? portfolioBias
          : null
      ) ??
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