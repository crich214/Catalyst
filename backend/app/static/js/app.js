import { loadRegime } from "./regime.js";
import { loadHealth } from "./health.js";
import { loadRadar } from "./radar.js";
import { loadEvents } from "./events.js";
import { loadSignals } from "./signals.js";
import { loadTicker } from "./company.js";

window.loadTicker = loadTicker;

document.getElementById("refreshRegime").addEventListener("click", loadRegime);
document.getElementById("refreshHealth").addEventListener("click", loadHealth);
document.getElementById("refreshRadar").addEventListener("click", loadRadar);
document.getElementById("refreshEvents").addEventListener("click", loadEvents);
document.getElementById("refreshSignals").addEventListener("click", loadSignals);
document.getElementById("analyzeTicker").addEventListener("click", () => loadTicker());

document.getElementById("tickerInput").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    loadTicker();
  }
});

async function bootCatalyst() {
  await loadRegime();
  await loadHealth();
  await loadRadar();
  await loadEvents();
  await loadSignals();
}

bootCatalyst();