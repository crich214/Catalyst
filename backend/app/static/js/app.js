import { loadRegime } from "./regime.js";
import { loadHealth } from "./health.js";
import { loadRadar } from "./radar.js";
import { loadEvents } from "./events.js";
import { loadSignals } from "./signals.js";
import { loadTicker } from "./company.js";


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
  bindButton("refreshEvents", loadEvents);
  bindButton("refreshSignals", loadSignals);

  bindButton("analyzeTicker", () => {
    loadTicker();
  });

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


async function bootCatalyst() {
  bindInterface();

  await Promise.allSettled([
    safeLoad("market regime", loadRegime),
    safeLoad("system health", loadHealth),
    safeLoad("opportunity board", loadRadar),
    safeLoad("event intelligence", loadEvents),
    safeLoad("signal engine", loadSignals),
  ]);
}


bootCatalyst();