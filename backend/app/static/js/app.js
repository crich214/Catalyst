import { loadRegime } from "./regime.js";
import { loadHealth } from "./health.js";
import { loadRadar } from "./radar.js";
import { loadEvents } from "./events.js";
import { loadSignals } from "./signals.js";
import { loadTicker } from "./company.js";
import { loadPortfolio } from "./portfolio.js";
import { loadPerformance } from "./performance.js";
import { loadJournal } from "./journal.js";


window.loadTicker = loadTicker;


function bindButton(id, handler) {
  const element = document.getElementById(id);

  if (element) {
    element.addEventListener("click", handler);
  }
}


function bindInterface() {
  bindButton("refreshRegime", loadRegime);
  bindButton("refreshHealth", loadHealth);
  bindButton("refreshRadar", loadRadar);
  bindButton("refreshPortfolio", loadPortfolio);
  bindButton("refreshPerformance", loadPerformance);
  bindButton("refreshJournal", loadJournal);
  bindButton("refreshEvents", loadEvents);
  bindButton("refreshSignals", loadSignals);

  bindButton("analyzeTicker", () => {
    loadTicker();
  });

  bindButton("refreshDashboard", refreshDashboard);

  const tickerInput = document.getElementById("tickerInput");

  if (tickerInput) {
    tickerInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        loadTicker();
      }
    });
  }
}


async function safeLoad(name, loader) {
  try {
    await loader();
  } catch (error) {
    console.error(`Catalyst failed to load ${name}:`, error);
  }
}


async function loadMorningBrief() {
  const brief = document.getElementById("morningBrief");

  if (!brief) {
    return;
  }

  brief.innerHTML = `
    <div class="loading">
      Preparing the Chairman's morning brief...
    </div>
  `;

  try {
    const [
      regimeResponse,
      portfolioResponse,
      radarResponse,
    ] = await Promise.all([
      fetch("/market-regime"),
      fetch("/portfolio/pilot"),
      fetch("/opportunities/live"),
    ]);

    if (
      !regimeResponse.ok ||
      !portfolioResponse.ok ||
      !radarResponse.ok
    ) {
      throw new Error(
        "One or more briefing data sources were unavailable."
      );
    }

    const regime = await regimeResponse.json();
    const portfolio = await portfolioResponse.json();
    const radar = await radarResponse.json();

    const actionable =
      radar.actionable_opportunities || [];

    const actionableTickers = actionable
      .slice(0, 5)
      .map((item) => item.ticker)
      .filter(Boolean);

    const cash = Number(portfolio.cash ?? 0);
    const positions = Array.isArray(portfolio.positions)
      ? portfolio.positions.length
      : 0;

    const regimeName =
      regime.regime ||
      regime.market_regime ||
      "Unknown";

    const riskLevel =
      regime.risk_level ||
      "Moderate";

    const recommendationText = actionableTickers.length
      ? `Current accumulation candidates: ${actionableTickers.join(", ")}.`
      : "No new companies currently meet Catalyst accumulation criteria.";

    brief.innerHTML = `
      <div class="brief-grid">
        <div class="brief-metric">
          <span>Market Regime</span>
          <strong>${regimeName}</strong>
        </div>

        <div class="brief-metric">
          <span>Macro Risk</span>
          <strong>${riskLevel}</strong>
        </div>

        <div class="brief-metric">
          <span>Portfolio Positions</span>
          <strong>${positions}</strong>
        </div>

        <div class="brief-metric">
          <span>Cash Available</span>
          <strong>$${cash.toFixed(2)}</strong>
        </div>
      </div>

      <div class="chairman-message">
        <strong>Today's Recommendation</strong>

        <p>
          ${recommendationText}
          Maintain selective deployment and preserve the current cash reserve
          unless a materially stronger opportunity emerges.
        </p>
      </div>
    `;
  } catch (error) {
    console.error("Morning Brief error:", error);

    brief.innerHTML = `
      <div class="error">
        <strong>Unable to prepare the morning brief.</strong>

        <div class="small">
          ${error.message ?? "Unknown error"}
        </div>
      </div>
    `;
  }
}


async function refreshDashboard() {
  await Promise.allSettled([
    safeLoad("morning brief", loadMorningBrief),
    safeLoad("market regime", loadRegime),
    safeLoad("system health", loadHealth),
    safeLoad("opportunity board", loadRadar),
    safeLoad("pilot portfolio", loadPortfolio),
    safeLoad("performance", loadPerformance),
    safeLoad("decision journal", loadJournal),
    safeLoad("event intelligence", loadEvents),
    safeLoad("signal engine", loadSignals),
  ]);
}


async function bootCatalyst() {
  bindInterface();
  await refreshDashboard();
}


bootCatalyst();