import yfinance as yf
from app.universe import (
    CATEGORY_MAP,
    FALLBACKS,
    HIGH_INSIDER_PLACEHOLDERS,
    HIGH_MACRO,
    HIGH_CATALYST,
    normalize_ticker,
)

def safe_float(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def get_live_stock(ticker: str):
    ticker = normalize_ticker(ticker)

    try:
        live = fetch_yfinance_stock(ticker)
        if live:
            return live
    except Exception:
        pass

    if ticker in FALLBACKS:
        return FALLBACKS[ticker]

    raise ValueError(f"No live or fallback data found for {ticker}")

def fetch_yfinance_stock(ticker: str):
    t = yf.Ticker(ticker)

    info = {}
    try:
        info = t.info or {}
    except Exception:
        info = {}

    fast = {}
    try:
        fast = dict(t.fast_info or {})
    except Exception:
        fast = {}

    hist_price = None
    try:
        hist = t.history(period="5d")
        if not hist.empty:
            hist_price = safe_float(hist["Close"].dropna().iloc[-1])
    except Exception:
        hist_price = None

    price = (
        safe_float(fast.get("last_price"))
        or safe_float(info.get("currentPrice"))
        or safe_float(info.get("regularMarketPrice"))
        or safe_float(info.get("previousClose"))
        or hist_price
    )

    if not price:
        return None

    fifty_two_high = (
        safe_float(info.get("fiftyTwoWeekHigh"))
        or safe_float(fast.get("year_high"))
    )

    market_cap = (
        safe_float(info.get("marketCap"))
        or safe_float(fast.get("market_cap"))
    )

    pe_ratio = safe_float(info.get("trailingPE"))

    free_cashflow = safe_float(info.get("freeCashflow"))
    fcf_yield = None
    warnings = []

    if free_cashflow is not None and market_cap:
        fcf_yield = (free_cashflow / market_cap) * 100
    else:
        warnings.append("FCF yield unavailable from live provider.")

    price_decline_pct = 0
    if fifty_two_high and fifty_two_high > 0:
        price_decline_pct = max(0, ((fifty_two_high - price) / fifty_two_high) * 100)
    else:
        warnings.append("52-week high unavailable from live provider.")

    sector = info.get("sector") or "Unknown"
    if sector == "Unknown":
        warnings.append("Sector unavailable from live provider.")

    company_name = info.get("longName") or info.get("shortName") or ticker
    intrinsic_value = estimate_intrinsic_value(price, pe_ratio, fcf_yield, price_decline_pct)

    return {
        "ticker": ticker,
        "company": company_name,
        "category": CATEGORY_MAP.get(ticker, "General Equity"),
        "sector": sector,
        "price": round(price, 2),
        "intrinsic_value": round(intrinsic_value, 2),
        "pe_ratio": pe_ratio,
        "fcf_yield": fcf_yield,
        "price_decline_pct": price_decline_pct,
        "market_cap": market_cap,
        "quality": estimate_quality_score(info),
        "insider": estimate_insider_score(ticker),
        "macro": estimate_macro_score(ticker),
        "catalyst": estimate_catalyst_score(ticker),
        "risk": estimate_risk_score(info, ticker),
        "data_status": "live" if not warnings else "partial_live",
        "data_warnings": warnings,
        "reason": build_reason(ticker, company_name, sector)
    }

def estimate_intrinsic_value(price, pe_ratio, fcf_yield, drawdown):
    premium = 1.0

    if pe_ratio is not None:
        if pe_ratio < 12:
            premium += 0.35
        elif pe_ratio < 20:
            premium += 0.20
        elif pe_ratio > 40:
            premium -= 0.10

    if fcf_yield is not None:
        if fcf_yield >= 6:
            premium += 0.25
        elif fcf_yield >= 3:
            premium += 0.10
        elif fcf_yield < 0:
            premium -= 0.25

    if drawdown >= 40:
        premium += 0.20
    elif drawdown >= 25:
        premium += 0.10

    return max(price * premium, price * 0.75)

def estimate_quality_score(info):
    score = 50
    profit_margins = safe_float(info.get("profitMargins"), 0)
    operating_margins = safe_float(info.get("operatingMargins"), 0)
    roe = safe_float(info.get("returnOnEquity"), 0)
    revenue_growth = safe_float(info.get("revenueGrowth"), 0)

    if profit_margins >= 0.20:
        score += 18
    elif profit_margins >= 0.10:
        score += 10
    elif profit_margins < 0:
        score -= 15

    if operating_margins >= 0.25:
        score += 14
    elif operating_margins >= 0.12:
        score += 8

    if roe >= 0.20:
        score += 10
    elif roe >= 0.10:
        score += 5

    if revenue_growth >= 0.15:
        score += 8
    elif revenue_growth >= 0.05:
        score += 4
    elif revenue_growth < 0:
        score -= 8

    return round(max(0, min(100, score)), 1)

def estimate_insider_score(ticker):
    return HIGH_INSIDER_PLACEHOLDERS.get(ticker, 40)

def estimate_macro_score(ticker):
    return HIGH_MACRO.get(ticker, 70)

def estimate_catalyst_score(ticker):
    return HIGH_CATALYST.get(ticker, 65)

def estimate_risk_score(info, ticker):
    score = 45
    beta = safe_float(info.get("beta"), 1)
    debt_to_equity = safe_float(info.get("debtToEquity"), 50)

    if beta and beta > 2:
        score += 25
    elif beta and beta > 1.4:
        score += 12
    elif beta and beta < 0.8:
        score -= 8

    if debt_to_equity and debt_to_equity > 200:
        score += 15
    elif debt_to_equity and debt_to_equity < 50:
        score -= 5

    if "Moonshot" in CATEGORY_MAP.get(ticker, ""):
        score += 25

    return round(max(0, min(100, score)), 1)

def build_reason(ticker, company_name, sector):
    category = CATEGORY_MAP.get(ticker, "General Equity")
    return f"{company_name} is classified as {category} within {sector}; live data is used for valuation and execution scoring when available."
