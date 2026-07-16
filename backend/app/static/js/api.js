async function parseResponse(response, fallbackMessage) {
  let data;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      fallbackMessage;

    throw new Error(detail);
  }

  return data;
}


export async function getMarketRegime() {
  const response = await fetch("/market-regime");

  return parseResponse(
    response,
    "Unable to load the current market regime."
  );
}


export async function getSystemHealth() {
  const response = await fetch("/system-health");

  return parseResponse(
    response,
    "Unable to load system health."
  );
}


export async function getRadar() {
  const response = await fetch("/opportunities/live");

  return parseResponse(
    response,
    "Unable to load the opportunity board."
  );
}


export async function getEvents() {
  const response = await fetch("/events");

  return parseResponse(
    response,
    "Unable to load event intelligence."
  );
}


export async function getSignals() {
  const response = await fetch("/signals");

  return parseResponse(
    response,
    "Unable to load signal intelligence."
  );
}


export async function getCompany(ticker) {
  const normalizedTicker = String(ticker || "")
    .trim()
    .toUpperCase();

  if (!normalizedTicker) {
    throw new Error("A ticker is required.");
  }

  const response = await fetch(
    `/live/${encodeURIComponent(normalizedTicker)}`
  );

  const data = await parseResponse(
    response,
    `Unable to load ${normalizedTicker}.`
  );

  return {
    res: response,
    data,
  };
}


export async function getCommittee(ticker) {
  const normalizedTicker = String(ticker || "")
    .trim()
    .toUpperCase();

  if (!normalizedTicker) {
    throw new Error("A ticker is required.");
  }

  const response = await fetch(
    `/committee/${encodeURIComponent(normalizedTicker)}`
  );

  const data = await parseResponse(
    response,
    `Unable to run the committee for ${normalizedTicker}.`
  );

  return {
    res: response,
    data,
  };
}


export async function getPortfolio() {
  const response = await fetch("/portfolio/pilot");

  return parseResponse(
    response,
    "Unable to load the pilot portfolio."
  );
}


export async function getPerformance() {
  const response = await fetch("/performance/pilot");

  return parseResponse(
    response,
    "Unable to load pilot performance."
  );
}


export async function getJournal(limit = 50) {
  const safeLimit = Math.max(
    1,
    Math.min(Number(limit) || 50, 500)
  );

  const response = await fetch(
    `/journal?limit=${safeLimit}`
  );

  return parseResponse(
    response,
    "Unable to load the decision journal."
  );
}


export async function recordJournalDecision(ticker) {
  const normalizedTicker = String(ticker || "")
    .trim()
    .toUpperCase();

  if (!normalizedTicker) {
    throw new Error("A ticker is required.");
  }

  const response = await fetch(
    `/journal/${encodeURIComponent(normalizedTicker)}`,
    {
      method: "POST",
    }
  );

  return parseResponse(
    response,
    `Unable to record a decision for ${normalizedTicker}.`
  );
}