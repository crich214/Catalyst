import { getCompany, getCommittee } from "./api.js";
import { fmtMoney } from "./utils.js";
import { renderCommittee } from "./committee.js";

export async function loadTicker(tickerOverride = null) {

    const input = document.getElementById("tickerInput");
    const ticker = (tickerOverride || input.value || "")
        .trim()
        .toUpperCase();

    input.value = ticker;

    const card = document.getElementById("resultCard");

    card.innerHTML = `
        <div class="loading">
            Running ${ticker} through the Catalyst Investment Committee...
        </div>
    `;

    try {

        const { res, data } = await getCompany(ticker);

        if (!res.ok) {
            card.innerHTML = `
                <div class="error">
                    ${data.detail}
                </div>
            `;
            return;
        }

        const committee = await getCommittee(ticker);

        renderCompany(card, data);

        renderCommittee(card, committee.data);

    }
    catch (err) {

        card.innerHTML = `
            <div class="error">
                Unable to connect to Catalyst.
            </div>
        `;

        console.error(err);

    }

}

export function renderCompany(card, data) {

    const ladder = data.accumulation_plan?.ladder || [];

    card.innerHTML = `

        <div class="reason">

            <div class="ticker">${data.ticker}</div>

            <h2>${data.company}</h2>

            <div class="small">

                ${data.category}

                •

                ${data.sector}

            </div>

        </div>

        <div class="score-row">

            <div class="score-box">
                <span>Rich Alpha</span>
                <strong>${data.adjusted_rich_alpha_score ?? data.rich_alpha_score}</strong>
            </div>

            <div class="score-box">
                <span>Conviction</span>
                <strong>${data.conviction_score}</strong>
            </div>

            <div class="score-box">
                <span>Risk</span>
                <strong>${data.risk_score}</strong>
            </div>

            <div class="score-box">
                <span>Recommendation</span>
                <strong>${data.recommendation}</strong>
            </div>

        </div>

        <div class="reason">

            <strong>Investment Thesis</strong>

            <br><br>

            ${data.top_reason}

        </div>

        <table>

            <tr>

                <th>Metric</th>

                <th>Value</th>

            </tr>

            <tr>

                <td>Price</td>

                <td>${fmtMoney(data.price)}</td>

            </tr>

            <tr>

                <td>Intrinsic Value</td>

                <td>${fmtMoney(data.intrinsic_value)}</td>

            </tr>

            <tr>

                <td>Market Cap</td>

                <td>${fmtMoney(data.market_cap)}</td>

            </tr>

            <tr>

                <td>P/E Ratio</td>

                <td>${data.pe_ratio ?? "N/A"}</td>

            </tr>

        </table>

        <h2 style="margin-top:25px">

            Accumulation Plan™

        </h2>

        <table>

            <tr>

                <th>Price Zone</th>

                <th>Action</th>

                <th>Target</th>

            </tr>

            ${ladder.map(item => `

                <tr>

                    <td>${item.price_zone}</td>

                    <td>${item.action}</td>

                    <td>${item.target_position}</td>

                </tr>

            `).join("")}

        </table>

    `;

}

window.loadTicker = loadTicker;