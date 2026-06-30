# Catalyst Step 6 — FRED Macro Engine

This release connects Catalyst to live macroeconomic data from FRED public CSV endpoints.

## What's new

- FRED macro connector
- Live/partial-live macro regime engine
- Federal Funds Rate
- 10Y Treasury
- 2Y Treasury
- Yield curve
- Unemployment
- Credit spreads
- VIX
- Macro data quality status
- System Health now shows Macro Data as Live

## Run on Mac

```bash
cd catalyst_step6_fred_macro
./launch_mac.command
```

## Run on Windows

```bat
launch_windows.bat
```

## Open UI

```text
http://127.0.0.1:8000
```

## Developer Docs

```text
http://127.0.0.1:8000/docs
```

## Test endpoint

```text
http://127.0.0.1:8000/market-regime
```

## Note

FRED data uses public CSV downloads. If offline or blocked, Catalyst falls back to internal values and labels the macro status as partial/live fallback.
