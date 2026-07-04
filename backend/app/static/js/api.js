export async function getMarketRegime() {
  const res = await fetch("/market-regime");
  return await res.json();
}

export async function getSystemHealth() {
  const res = await fetch("/system-health");
  return await res.json();
}

export async function getRadar() {
  const res = await fetch("/opportunities/live");
  return await res.json();
}

export async function getEvents() {
  const res = await fetch("/events");
  return await res.json();
}

export async function getSignals() {
  const res = await fetch("/signals");
  return await res.json();
}

export async function getCompany(ticker) {
  const res = await fetch(`/live/${ticker}`);
  const data = await res.json();
  return { res, data };
}

export async function getCommittee(ticker) {
  const res = await fetch(`/committee/${ticker}`);
  const data = await res.json();
  return { res, data };
}