import { getPerformance } from "./api.js";


function formatCurrency(value) {
  const number = Number(value ?? 0);

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(number);
}


function formatPercent(value) {
  const number = Number(value ?? 0);
  const sign = number > 0 ? "+" : "";

  return `${sign}${number.toFixed(2)}%`;
}


function returnClass(value) {
  const number = Number(value ?? 0);

  if (number > 0) {
    return "positive";
  }

  if (number < 0) {
    return "negative";
  }

  return "neutral";
}


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function renderBenchmarkCard(benchmark) {
  const name =
    benchmark.name ??
    benchmark.ticker ??
    "Benchmark";

  const ticker =
    benchmark.ticker ??
    "";

  const returnPct = Number(
    benchmark.return_pct ?? 0
  );

  const startPrice = Number(
    benchmark.start_price ?? 0
  );

  const currentPrice = Number(
    benchmark.current_price ?? 0
  );

  return `
    <div class="metric-card">
      <span>${escapeHtml(name)}</span>

      <strong class="${returnClass(returnPct)}">
        ${formatPercent(returnPct)}
      </strong>

      <div class="small">
        ${escapeHtml(ticker)}
      </div>

      <div class="small">
        ${formatCurrency(startPrice)}
        →
        ${formatCurrency(currentPrice)}
      </div>
    </div>
  `;
}


function renderRelativePerformance(relativePerformance) {
  if (
    !Array.isArray(relativePerformance) ||
    relativePerformance.length === 0
  ) {
    return `
      <div class="empty">
        Relative benchmark performance is not available yet.
      </div>
    `;
  }

  const rows = relativePerformance
    .map((item) => {
      const benchmarkReturn = Number(
        item.benchmark_return_pct ?? 0
      );

      const outperformance = Number(
        item.outperformance_pct ?? 0
      );

      return `
        <tr>
          <td>
            <strong>
              ${escapeHtml(
                item.benchmark ?? "Benchmark"
              )}
            </strong>
          </td>

          <td class="${returnClass(benchmarkReturn)}">
            ${formatPercent(benchmarkReturn)}
          </td>

          <td class="${returnClass(outperformance)}">
            ${formatPercent(outperformance)}
          </td>
        </tr>
      `;
    })
    .join("");

  return `
    <div class="performance-comparison">
      <h3>Relative Performance</h3>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Benchmark</th>
              <th>Benchmark Return</th>
              <th>Catalyst Alpha</th>
            </tr>
          </thead>

          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    </div>
  `;
}


function renderPositionPerformance(positions) {
  if (
    !Array.isArray(positions) ||
    positions.length === 0
  ) {
    return "";
  }

  const sortedPositions = [...positions].sort(
    (left, right) =>
      Number(right.unrealized_return_pct ?? 0) -
      Number(left.unrealized_return_pct ?? 0)
  );

  const rows = sortedPositions
    .map((position) => {
      const returnPct = Number(
        position.unrealized_return_pct ?? 0
      );

      const gainLoss = Number(
        position.unrealized_gain_loss ?? 0
      );

      return `
        <tr
          class="clickable"
          data-ticker="${escapeHtml(
            position.ticker
          )}"
        >
          <td>
            <strong>
              ${escapeHtml(position.ticker)}
            </strong>
          </td>

          <td>
            ${formatCurrency(
              position.current_value
            )}
          </td>

          <td class="${returnClass(gainLoss)}">
            ${formatCurrency(gainLoss)}
          </td>

          <td class="${returnClass(returnPct)}">
            ${formatPercent(returnPct)}
          </td>
        </tr>
      `;
    })
    .join("");

  return `
    <div class="performance-comparison">
      <h3>Position Performance</h3>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Current Value</th>
              <th>Gain / Loss</th>
              <th>Return</th>
            </tr>
          </thead>

          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    </div>
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


export async function loadPerformance() {
  const panel = document.getElementById(
    "performancePanel"
  );

  if (!panel) {
    return;
  }

  panel.innerHTML = `
    <div class="loading">
      Loading pilot performance...
    </div>
  `;

  try {
    const performance = await getPerformance();

    const startingCapital = Number(
      performance.starting_capital ?? 0
    );

    const totalValue = Number(
      performance.total_value ?? 0
    );

    const investedValue = Number(
      performance.invested_value ?? 0
    );

    const cash = Number(
      performance.cash ?? 0
    );

    const totalGainLoss = Number(
      performance.total_gain_loss ?? 0
    );

    const totalReturnPct = Number(
      performance.total_return_pct ?? 0
    );

    const benchmarks = Array.isArray(
      performance.benchmarks
    )
      ? performance.benchmarks
      : [];

    const benchmarkCards = benchmarks.length
      ? benchmarks
          .map(renderBenchmarkCard)
          .join("")
      : `
          <div class="empty">
            Benchmark data is not currently available.
          </div>
        `;

    panel.innerHTML = `
      <div class="portfolio-summary-grid">
        <div class="metric-card">
          <span>Starting Capital</span>

          <strong>
            ${formatCurrency(startingCapital)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Current Value</span>

          <strong>
            ${formatCurrency(totalValue)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Total Gain / Loss</span>

          <strong class="${returnClass(totalGainLoss)}">
            ${formatCurrency(totalGainLoss)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Total Return</span>

          <strong class="${returnClass(totalReturnPct)}">
            ${formatPercent(totalReturnPct)}
          </strong>
        </div>
      </div>

      <div class="portfolio-summary-grid performance-benchmarks">
        <div class="metric-card">
          <span>Invested Value</span>

          <strong>
            ${formatCurrency(investedValue)}
          </strong>
        </div>

        <div class="metric-card">
          <span>Cash Reserve</span>

          <strong>
            ${formatCurrency(cash)}
          </strong>
        </div>

        ${benchmarkCards}
      </div>

      ${renderRelativePerformance(
        performance.relative_performance
      )}

      ${renderPositionPerformance(
        performance.positions
      )}
    `;

    bindPositionClicks(panel);
  } catch (error) {
    console.error(
      "Performance dashboard error:",
      error
    );

    panel.innerHTML = `
      <div class="error">
        <strong>
          Unable to load pilot performance.
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