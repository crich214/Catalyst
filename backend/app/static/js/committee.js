export function renderCommittee(card, data) {
  const decision = data.decision || {};
  const views = decision.member_views || [];
  const voteSummary = buildVoteSummary(views);

  const html = `
    <section class="committee-chamber">
      <div class="committee-eyebrow">Investment Committee</div>

      <div class="chairman-panel">
        <div>
          <div class="small">Chairman's Recommendation</div>
          <h2 class="chairman-recommendation">${decision.recommendation || "N/A"}</h2>
        </div>

        <div class="chairman-metrics">
          <div>
            <span>Conviction</span>
            <strong>${decision.conviction || "N/A"}</strong>
          </div>
          <div>
            <span>Vote</span>
            <strong>${voteSummary}</strong>
          </div>
        </div>
      </div>

      <div class="chairman-remarks">
        <strong>Chairman's Remarks</strong>
        <p>${decision.chairman_summary || "No chairman summary available."}</p>
      </div>

      <div class="committee-grid">
        ${views.map(view => renderMemberCard(view)).join("")}
      </div>
    </section>
  `;

  card.innerHTML = html + card.innerHTML;
}

function buildVoteSummary(views) {
  const supportive = views.filter(v =>
    ["Bullish", "Constructive"].includes(v.stance)
  ).length;

  return `${supportive}-${views.length - supportive}`;
}

function renderMemberCard(view) {
  return `
    <div class="committee-member">
      <div class="member-header">
        <div>
          <div class="member-name">${view.member}</div>
          <div class="member-stance">${view.stance}</div>
        </div>
        <div class="member-score">${view.score}</div>
      </div>

      <div class="member-summary">${view.summary}</div>

      <div class="member-notes">
        <div>
          <strong>Positives</strong>
          <ul>
            ${(view.positives || []).map(item => `<li>${item}</li>`).join("") || "<li>None</li>"}
          </ul>
        </div>

        <div>
          <strong>Concerns</strong>
          <ul>
            ${(view.concerns || []).map(item => `<li>${item}</li>`).join("") || "<li>None</li>"}
          </ul>
        </div>
      </div>
    </div>
  `;
}