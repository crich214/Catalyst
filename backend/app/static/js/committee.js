export function renderCommittee(card, data) {
  const decision = data.decision || {};
  const views = decision.analyst_reviews || [];
  const voteSummary = buildVoteSummary(views);

  const html = `
    <section class="committee-chamber">
      <div class="committee-eyebrow">Investment Committee</div>

      <div class="chairman-panel">
        <div>
          <div class="small">Chairman's Recommendation</div>
          <h2 class="chairman-recommendation">
            ${decision.final_recommendation || "N/A"}
          </h2>
          <div class="committee-action">
            Committee Action: ${decision.committee_action || "AFFIRM"}
          </div>
        </div>

        <div class="chairman-metrics">
          <div>
            <span>Conviction</span>
            <strong>${decision.conviction ?? "N/A"}</strong>
          </div>
          <div>
            <span>Committee Vote</span>
            <strong>${voteSummary}</strong>
          </div>
        </div>
      </div>

      <div class="chairman-remarks">
        <strong>Chairman's Memorandum</strong>
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
  const supportive = views.filter(view =>
    ["Supportive", "Constructive"].includes(view.stance)
  ).length;

  const cautious = views.filter(view =>
    ["Cautious", "Restrictive", "Defensive"].includes(view.stance)
  ).length;

  const neutral = Math.max(0, views.length - supportive - cautious);

  return `${supportive} supportive / ${neutral} neutral / ${cautious} cautious`;
}

function renderMemberCard(view) {
  return `
    <div class="committee-member">
      <div class="member-header">
        <div>
          <div class="member-name">${view.member || "Committee Member"}</div>
          <div class="member-domain">${view.domain || "General"}</div>
          <div class="member-stance">${view.stance || "N/A"}</div>
          <div class="member-assessment">${view.assessment || "No assessment"}</div>
        </div>

        <div class="member-score">
          ${view.confidence ?? "N/A"}%
        </div>
      </div>

      <div class="member-role">
        ${view.role || ""}
      </div>

      <div class="member-summary">
        ${view.summary || "No summary available."}
      </div>

      <div class="member-notes">
        <div>
          <strong>Positives</strong>
          <ul>
            ${renderList(view.positives)}
          </ul>
        </div>

        <div>
          <strong>Concerns</strong>
          <ul>
            ${renderList(view.concerns)}
          </ul>
        </div>
      </div>
    </div>
  `;
}

function renderList(items) {
  if (!items || items.length === 0) {
    return "<li>None</li>";
  }

  return items.map(item => `<li>${item}</li>`).join("");
}