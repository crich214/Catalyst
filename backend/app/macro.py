import requests
import pandas as pd
from io import StringIO
from datetime import datetime

FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

SERIES = {
    "fed_funds": {
        "id": "FEDFUNDS",
        "name": "Federal Funds Rate",
        "unit": "%"
    },
    "ten_year": {
        "id": "DGS10",
        "name": "10-Year Treasury",
        "unit": "%"
    },
    "two_year": {
        "id": "DGS2",
        "name": "2-Year Treasury",
        "unit": "%"
    },
    "cpi": {
        "id": "CPIAUCSL",
        "name": "CPI Index",
        "unit": "Index"
    },
    "unemployment": {
        "id": "UNRATE",
        "name": "Unemployment Rate",
        "unit": "%"
    },
    "credit_spread": {
        "id": "BAA10Y",
        "name": "BAA Corporate Spread over 10Y",
        "unit": "%"
    },
    "vix": {
        "id": "VIXCLS",
        "name": "VIX",
        "unit": "Index"
    },
}

FALLBACK_VALUES = {
    "fed_funds": {"value": 4.75, "date": "fallback", "status": "fallback"},
    "ten_year": {"value": 4.45, "date": "fallback", "status": "fallback"},
    "two_year": {"value": 4.60, "date": "fallback", "status": "fallback"},
    "cpi": {"value": 318.0, "date": "fallback", "status": "fallback"},
    "unemployment": {"value": 4.1, "date": "fallback", "status": "fallback"},
    "credit_spread": {"value": 2.1, "date": "fallback", "status": "fallback"},
    "vix": {"value": 18.0, "date": "fallback", "status": "fallback"},
}

def fetch_fred_series(series_id):
    url = FRED_BASE + series_id
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    value_col = series_id

    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])

    if df.empty:
        raise ValueError(f"No usable FRED data for {series_id}")

    last = df.iloc[-1]
    return {
        "value": float(last[value_col]),
        "date": str(last["observation_date"]),
        "status": "live"
    }

def get_macro_data():
    output = {}

    for key, meta in SERIES.items():
        try:
            point = fetch_fred_series(meta["id"])
        except Exception:
            point = FALLBACK_VALUES[key]

        output[key] = {
            **point,
            "series_id": meta["id"],
            "name": meta["name"],
            "unit": meta["unit"]
        }

    return output

def classify_macro_regime(data):
    fed = data["fed_funds"]["value"]
    ten = data["ten_year"]["value"]
    two = data["two_year"]["value"]
    unemployment = data["unemployment"]["value"]
    spread = data["credit_spread"]["value"]
    vix = data["vix"]["value"]

    curve = ten - two

    score = 50
    flags = []

    if fed >= 4.5:
        score += 15
        flags.append("Restrictive Fed policy")
    elif fed <= 2.0:
        score -= 10
        flags.append("Easy Fed policy")

    if curve < 0:
        score += 10
        flags.append("Inverted yield curve")
    elif curve > 1:
        score -= 5
        flags.append("Steep yield curve")

    if unemployment >= 5:
        score += 15
        flags.append("Labor market stress")
    elif unemployment <= 4:
        score -= 5
        flags.append("Tight labor market")

    if spread >= 3:
        score += 15
        flags.append("Credit stress")
    elif spread <= 1.5:
        score -= 5
        flags.append("Benign credit spreads")

    if vix >= 25:
        score += 10
        flags.append("Elevated volatility")
    elif vix <= 15:
        score -= 5
        flags.append("Low volatility")

    score = max(0, min(100, round(score)))

    if fed >= 4.5 and curve < 0:
        regime = "Higher-for-Longer / Late Cycle"
    elif spread >= 3 or unemployment >= 5:
        regime = "Credit Stress / Defensive"
    elif fed <= 2 and vix <= 18:
        regime = "Liquidity Expansion"
    else:
        regime = "Balanced / Watchful"

    if fed >= 4.0:
        favored = ["Cash-Flow Dislocations", "Financials", "Defense", "Power & Grid", "Quality Compounders"]
        cautious = ["Highly Levered Growth", "Low-Margin Consumer", "Speculative Long-Duration Assets"]
    elif fed <= 2.0:
        favored = ["Growth", "Innovation", "Small Caps", "Software", "Speculative Innovation"]
        cautious = ["Cash Drag", "Overly Defensive Allocations"]
    else:
        favored = ["Quality Compounders", "AI Infrastructure", "Selective Dislocations"]
        cautious = ["Weak Balance Sheets", "Value Traps"]

    return {
        "regime": regime,
        "regime_score": score,
        "risk_level": "High" if score >= 75 else "Medium-High" if score >= 60 else "Moderate" if score >= 40 else "Low",
        "flags": flags,
        "yield_curve": round(curve, 2),
        "favored_themes": favored,
        "cautious_themes": cautious,
        "summary": build_summary(regime, score, flags),
        "portfolio_bias": {
            "compounders": "Overweight quality" if score >= 50 else "Balanced",
            "dislocations": "Overweight selectively" if score >= 50 else "Selective",
            "moonshots": "Small basket only" if score >= 50 else "Moderate basket acceptable",
            "cash": "Maintain dry powder" if score >= 60 else "Deploy gradually"
        }
    }

def build_summary(regime, score, flags):
    if flags:
        flag_text = ", ".join(flags[:4])
    else:
        flag_text = "no major stress signals"

    return (
        f"Catalyst classifies the current macro regime as {regime}. "
        f"The macro risk score is {score}/100, driven by {flag_text}. "
        "This regime influences sector preferences, score weights, and position sizing."
    )

def macro_payload():
    data = get_macro_data()
    regime = classify_macro_regime(data)

    live_count = len([v for v in data.values() if v["status"] == "live"])
    fallback_count = len([v for v in data.values() if v["status"] != "live"])

    return {
        **regime,
        "data": data,
        "data_quality": {
            "total_series": len(data),
            "live": live_count,
            "fallback": fallback_count,
            "status": "live" if fallback_count == 0 else "partial_live"
        },
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
