import {
  getPortfolio,
  getPerformance,
} from "./api.js";


function formatCurrency(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(number);
}


function formatNumber(value, digits = 2) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  return number.toFixed(digits);
}


function formatPercent(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  const sign = number > 0 ? "+" : "";

  return `${sign}${number.toFixed(2)}%`;
}


function returnClass(value) {
  const number = Number(value);

  if (!Number.isFinite(number) || number === 0) {
    return "neutral";
  }

  if (number > 0) {
    return "positive";
  }

  return "negative";
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


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function firstFiniteNumber(...values) {
  for (const value of values) {
    const number = Number(value);

    if (Number.isFinite(number)) {
      return number;
    }
  }

  return null;
}


function normalizePerformancePositions(performance) {
  const candidates = [
    performance?.positions,
    performance?.position_performance,
    performance?.holdings,
    performance?.portfolio?.positions,
    performance?.performance?.positions,
  ];

  return candidates.find(Array.isArray) ?? [];
}


function findPerformancePosition(
  portfolioPosition,
  performancePositions
) {
  const ticker = String(
    portfolioPosition?.ticker ?? ""
  ).toUpperCase();

  return performancePositions.find(
    (position) =>
      String(position?.ticker ?? "").toUpperCase() === ticker
  );
}


function mergePositionData(
  portfolioPosition,
  performancePositions
) {
  const livePosition = findPerformancePosition(
    portfolioPosition,
    performancePositions
  );

  return {
    ...portfolioPosition,

    current_price: firstFiniteNumber(
      livePosition?.current_price,
      livePosition?.market_price,
      livePosition?.price,
      portfolioPosition?.current_price,
      portfolioPosition?.entry_price
    ),

    current_value: firstFiniteNumber(
      livePosition?.current_value,
      livePosition?.market_value,
      livePosition?.position_value,
      portfolioPosition?.current_value
    ),

    unrealized_gain_loss: firstFiniteNumber(
      livePosition?.unrealized_gain_loss,
      livePosition?.gain_loss,
      livePosition?.profit_loss,
      portfolioPosition?.unrealized_gain_loss
    ),

    unrealized_return_pct: firstFiniteNumber(
      livePosition?.unrealized_return_pct,
      livePosition?.return_pct,
      livePosition?.gain_loss_pct,
      livePosition?.performance_pct,
      portfolioPosition?.unrealized_return_pct,
      0
    ),
  };
}


function renderPositionRow(position) {
  const ticker = String(
    position.ticker ?? ""
  ).toUpperCase();

  const company =
    position.company ??
    position.company_name ??
    ticker;

  const shares = firstFiniteNumber(
    position.shares,
    position.quantity,
    0
  );

  const entryPrice = firstFiniteNumber(
    position.entry_price,
    position.average_cost,
    position.cost_basis_per_share,
    0
  );

  const currentPrice = firstFiniteNumber(
    position.current_price,
    entryPrice,
    0
  );

  const returnPct = firstFiniteNumber(
    position.unrealized_return_pct,
    0
  );

  const recommendation = String(
    position.recommendation ?? "WATCH"
  ).toUpperCase();

  return `
    <tr
      class="clickable"
      data-ticker="${escapeHtml(ticker)}"
    >
      <td>
        <strong>${escapeHtml(ticker)}</strong>
      </td>

      <td>
        <div>${escapeHtml(company)}</div>
      </td>

      <td>${formatNumber(shares, 2)}</td>

      <td>${formatCurrency(entryPrice)}</td>

      <td>${formatCurrency(currentPrice)}</td>

      <td class="${returnClass(returnPct)}">
        ${formatPercent(returnPct)}
      </td>

      <td>
        ${formatNumber(
          position.rich_alpha_score,
          1
        )}
      </td>

      <td>
        <span
          class="rec ${recommendationClass(
            recommendation
          )}"
        >
          ${escapeHtml(recommendation)}
        </span>
      </td>
    </tr>
  `;
}


function bindPositionClicks(container) {
  container
    .querySelectorAll("[data-ticker]")
    .forEach((row) => {
      row.addEventListener("click", () => {
        const ticker = row.dataset.ticker;

        if (
          ticker &&
          typeof window.loadTicker === "function"
        ) {
          window.loadTicker(ticker);
        }
      });
    });
}


export async function loadPortfolio() {
  const summary = document.getElementById(
    "portfolioSummary"
  );

  const positions = document.getElementById(
    "portfolioPositions"
  );

  if (!summary || !positions) {
    return;
  }

  summary.innerHTML = `
    <div class="loading">
      Loading pilot portfolio...
    </div>
  `;

  positions.innerHTML = `
    <div class="loading">
      Loading current positions...
    </div>
  `;

  try {
    const [
      portfolio,
      performance,
    ] = await Promise.all([
      getPortfolio(),
      getPerformance(),
    ]);

    const startingCapital = firstFiniteNumber(
      performance?.starting_capital,
      performance?.initial_capital,
      performance?.portfolio?.starting_capital,
      portfolio?.starting_capital,
      0
    );

    const investedCapital = firstFiniteNumber(
      portfolio?.invested_capital,
      portfolio?.cost_basis,
      performance?.invested_capital,
      performance?.cost_basis,
      0
    );

    const cash = firstFiniteNumber(
      performance?.cash,
      performance?.cash_balance,
      performance?.portfolio?.cash,
      portfolio?.cash,
      portfolio?.starting_cash,
      0
    );

    const investedValue = firstFiniteNumber(
      performance?.invested_value,
      performance?.current_invested_value,
      performance?.market_value,
      performance?.positions_value,
      performance?.portfolio?.invested_value
    );

    const portfolioValue = firstFiniteNumber(
      performance?.current_portfolio_value,
      performance?.portfolio_value,
      performance?.current_value,
      performance?.total_value,
      performance?.ending_value,
      performance?.portfolio?.total_value,
      investedValue != null
        ? investedValue + cash
        : null,
      startingCapital
    );

    const reportedGainLoss = firstFiniteNumber(
      performance?.total_gain_loss,
      performance?.gain_loss,
      performance?.profit_loss,
      performance?.unrealized_gain_loss,
      performance?.portfolio?.total_gain_loss
    );

    const totalGainLoss =
      reportedGainLoss ??
      (
        portfolioValue != null &&
        startingCapital != null
          ? portfolioValue - startingCapital
          : 0
      );

    const reportedReturnPct = firstFiniteNumber(
      performance?.total_return_pct,
      performance?.return_pct,
      performance?.portfolio_return_pct,
      performance?.performance_pct,
      performance?.portfolio?.total_return_pct
    );

    const totalReturnPct =
      reportedReturnPct ??
      (
        startingCapital
          ? (
              totalGainLoss /
              startingCapital
            ) * 100
          : 0
      );

    const cashReservePct = firstFiniteNumber(
      performance?.cash_reserve_pct,
      portfolio?.cash_reserve_pct,
      startingCapital
        ? (cash / startingCapital) * 100
        : 0
    );

    const displayedInvestedValue =
      investedValue ??
      (
        portfolioValue != null
          ? portfolioValue - cash
          : investedCapital
      );

    summary.innerHTML = `
      <div class="portfolio-summary-grid">
        <div class="metric-card">
          <span>Portfolio Value</span>

          <strong>
            ${formatCurrency(portfolioValue)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Invested Value</span>

          <strong>
            ${formatCurrency(
              displayedInvestedValue
            )}
          </strong>

          <div class="small">
            Cost basis:
            ${formatCurrency(investedCapital)}
          </div>
        </div>

        <div class="metric-card">
          <span>Cash Reserve</span>

          <strong>
            ${formatCurrency(cash)}
          </strong>

          <div class="small">
            ${formatPercent(cashReservePct)}
          </div>
        </div>

        <div class="metric-card">
          <span>Total Return</span>

          <strong
            class="${returnClass(
              totalReturnPct
            )}"
          >
            ${formatPercent(totalReturnPct)}
          </strong>

          <div
            class="small ${returnClass(
              totalGainLoss
            )}"
          >
            ${formatCurrency(totalGainLoss)}
          </div>
        </div>
      </div>
    `;

    const portfolioPositions = Array.isArray(
      portfolio?.positions
    )
      ? portfolio.positions
      : [];

    if (portfolioPositions.length === 0) {
      positions.innerHTML = `
        <div class="empty">
          The pilot portfolio does not contain any positions.
        </div>
      `;

      return;
    }

    const performancePositions =
      normalizePerformancePositions(
        performance
      );

    const mergedPositions =
      portfolioPositions.map(
        (position) =>
          mergePositionData(
            position,
            performancePositions
          )
      );

    const rows = mergedPositions
      .map(renderPositionRow)
      .join("");

    positions.innerHTML = `
      <div class="table-wrap">
        <table class="portfolio-table">
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Company</th>
              <th>Shares</th>
              <th>Entry</th>
              <th>Current</th>
              <th>Return</th>
              <th>Rich Alpha</th>
              <th>Recommendation</th>
            </tr>
          </thead>

          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;

    bindPositionClicks(positions);
  } catch (error) {
    console.error(
      "Pilot portfolio dashboard error:",
      error
    );

    summary.innerHTML = `
      <div class="error">
        <strong>
          Unable to load the pilot portfolio.
        </strong>

        <div class="small">
          ${escapeHtml(
            error?.message ??
            "Unknown error"
          )}
        </div>
      </div>
    `;

    positions.innerHTML = `
      <div class="error">
        Position data is unavailable.
      </div>
    `;
  }
}