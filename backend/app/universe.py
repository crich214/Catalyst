TICKER_ALIASES = {
    "FI": "FISV",
    "GOOG": "GOOGL",
    "BRK.B": "BRK-B",
    "BRK/B": "BRK-B",
}

CORE_UNIVERSE = [
    # AI Compounders
    "GOOGL", "MSFT", "NVDA", "META", "AMZN", "AVGO", "AAPL", "AMD", "ORCL", "PLTR",
    "NOW", "CRM", "SNOW", "CRWD", "NET", "ANET", "TSM", "ASML", "AMAT", "MU",

    # Power / Grid / AI Infrastructure
    "CEG", "GEV", "ETN", "PWR", "VST", "NEE", "DUK", "SO", "VRT", "HUBB",

    # Copper / Commodities / Energy
    "FCX", "SCCO", "XOM", "OXY", "CVX", "SLB", "LNG", "COP",

    # Defense / Aerospace / Space
    "RTX", "LMT", "NOC", "GD", "LHX", "HII", "RKLB", "LUNR", "ASTS",

    # Financials / Higher-for-Longer
    "BAC", "JPM", "GS", "MS", "SCHW", "C", "AXP", "BRK-B",

    # Dislocation / Turnaround
    "FISV", "UNH", "NKE", "DIS", "PYPL", "CVS", "TGT", "EL", "INTC", "SBUX",

    # Moonshots
    "SMR", "RXRX", "IONQ", "RGTI", "QBTS", "ACHR", "JOBY", "SERV", "DNA"
]

CATEGORY_MAP = {
    # AI Compounders
    "GOOGL": "Premium Compounder / AI",
    "MSFT": "Premium Compounder / AI",
    "NVDA": "Premium Compounder / AI Infrastructure",
    "META": "Premium Compounder / AI",
    "AMZN": "Premium Compounder / AI",
    "AVGO": "AI Infrastructure",
    "AAPL": "Premium Compounder",
    "AMD": "AI Semiconductor",
    "ORCL": "AI Infrastructure / Cloud",
    "PLTR": "Defense / AI",
    "NOW": "Enterprise AI / Software",
    "CRM": "Enterprise Software / AI",
    "SNOW": "Data Cloud / AI",
    "CRWD": "Cybersecurity / AI",
    "NET": "Internet Infrastructure / AI",
    "ANET": "AI Networking",
    "TSM": "Semiconductor Foundry",
    "ASML": "Semiconductor Equipment",
    "AMAT": "Semiconductor Equipment",
    "MU": "AI Memory",

    # Power
    "CEG": "AI Infrastructure / Power",
    "GEV": "AI Infrastructure / Grid",
    "ETN": "AI Infrastructure / Grid",
    "PWR": "AI Infrastructure / Grid",
    "VST": "AI Infrastructure / Power",
    "NEE": "Power / Utilities",
    "DUK": "Power / Utilities",
    "SO": "Power / Utilities",
    "VRT": "AI Data Center Infrastructure",
    "HUBB": "Electrical Infrastructure",

    # Commodities / Energy
    "FCX": "Copper / Electrification",
    "SCCO": "Copper / Electrification",
    "XOM": "Energy / Geopolitics",
    "OXY": "Energy / Geopolitics",
    "CVX": "Energy / Geopolitics",
    "SLB": "Energy Services",
    "LNG": "LNG / Energy Infrastructure",
    "COP": "Energy / Geopolitics",

    # Defense
    "RTX": "Defense / Geopolitics",
    "LMT": "Defense / Geopolitics",
    "NOC": "Defense / Geopolitics",
    "GD": "Defense / Geopolitics",
    "LHX": "Defense / Communications",
    "HII": "Defense / Shipbuilding",
    "RKLB": "Moonshot / Space",
    "LUNR": "Moonshot / Space Infrastructure",
    "ASTS": "Moonshot / Satellite Communications",

    # Financials
    "BAC": "Financials / Higher Rates",
    "JPM": "Financials / Quality Bank",
    "GS": "Financials / Capital Markets",
    "MS": "Financials / Wealth Management",
    "SCHW": "Financials / Brokerage",
    "C": "Financials / Turnaround",
    "AXP": "Financials / Premium Consumer",
    "BRK-B": "Quality Compounder / Holding Company",

    # Dislocations
    "FISV": "Compounder on Sale / Dislocation",
    "UNH": "Dislocation / Healthcare",
    "NKE": "Dislocation / Consumer Brand",
    "DIS": "Dislocation / Media",
    "PYPL": "Dislocation / Payments",
    "CVS": "Dislocation / Healthcare",
    "TGT": "Dislocation / Retail",
    "EL": "Dislocation / Consumer Brand",
    "INTC": "Turnaround / Semiconductor",
    "SBUX": "Dislocation / Consumer Brand",

    # Moonshots
    "SMR": "Moonshot / Nuclear",
    "RXRX": "Moonshot / AI Drug Discovery",
    "IONQ": "Moonshot / Quantum",
    "RGTI": "Moonshot / Quantum",
    "QBTS": "Moonshot / Quantum",
    "ACHR": "Moonshot / eVTOL",
    "JOBY": "Moonshot / eVTOL",
    "SERV": "Moonshot / Robotics",
    "DNA": "Moonshot / Synthetic Biology",
}

HIGH_INSIDER_PLACEHOLDERS = {
    "FISV": 95,
    "FI": 95,
    "RXRX": 50,
    "SMR": 30,
    "SERV": 35,
    "PYPL": 45,
    "UNH": 35,
    "NKE": 35,
}

HIGH_MACRO = {
    "CEG": 96, "GEV": 95, "ETN": 92, "PWR": 90, "VST": 93, "VRT": 94, "HUBB": 90,
    "FCX": 90, "SCCO": 88,
    "RTX": 88, "LMT": 86, "NOC": 86, "GD": 84, "LHX": 84, "HII": 82,
    "NVDA": 88, "AVGO": 87, "PLTR": 86, "ANET": 88, "TSM": 84, "ASML": 84,
    "SMR": 94, "LNG": 88, "XOM": 82, "OXY": 82
}

HIGH_CATALYST = {
    "FISV": 86, "GOOGL": 90, "MSFT": 86, "NVDA": 88, "META": 82,
    "CEG": 91, "GEV": 88, "VRT": 88, "SMR": 90, "RXRX": 86,
    "RKLB": 85, "LUNR": 84, "ACHR": 80, "IONQ": 82, "RGTI": 80,
    "QBTS": 80, "SERV": 82, "ASTS": 84, "PLTR": 86
}

FALLBACKS = {
    "FISV": {
        "ticker": "FISV",
        "company": "Fiserv",
        "category": "Compounder on Sale / Dislocation",
        "sector": "Financial Technology",
        "price": 49.00,
        "intrinsic_value": 78.00,
        "pe_ratio": 9.3,
        "fcf_yield": 8.2,
        "price_decline_pct": 42.0,
        "market_cap": 30000000000,
        "quality": 84,
        "insider": 95,
        "macro": 70,
        "catalyst": 86,
        "risk": 48,
        "data_status": "fallback",
        "data_warnings": ["Live provider unavailable; using Catalyst fallback profile."],
        "reason": "Fallback profile: Fiserv is classified as a dislocation candidate due to sharp drawdown, free-cash-flow generation, and insider buying."
    },
    "GOOGL": {
        "ticker": "GOOGL",
        "company": "Alphabet Inc.",
        "category": "Premium Compounder / AI",
        "sector": "Technology",
        "price": 180.00,
        "intrinsic_value": 225.00,
        "pe_ratio": 21,
        "fcf_yield": 4.2,
        "price_decline_pct": 12,
        "market_cap": 2300000000000,
        "quality": 97,
        "insider": 25,
        "macro": 86,
        "catalyst": 90,
        "risk": 30,
        "data_status": "fallback",
        "data_warnings": ["Live provider unavailable; using Catalyst fallback profile."],
        "reason": "Fallback profile: Alphabet is classified as a premium AI compounder with exceptional business quality and multiple long-term growth vectors."
    },
    "AAPL": {
        "ticker": "AAPL",
        "company": "Apple Inc.",
        "category": "Premium Compounder",
        "sector": "Technology",
        "price": 205.00,
        "intrinsic_value": 215.00,
        "pe_ratio": 30,
        "fcf_yield": 3.4,
        "price_decline_pct": 10,
        "market_cap": 3100000000000,
        "quality": 94,
        "insider": 20,
        "macro": 70,
        "catalyst": 72,
        "risk": 32,
        "data_status": "fallback",
        "data_warnings": ["Live provider unavailable; using Catalyst fallback profile."],
        "reason": "Fallback profile: Apple is classified as a premium compounder with high quality, though valuation discipline matters."
    },
    "NVDA": {
        "ticker": "NVDA",
        "company": "NVIDIA Corporation",
        "category": "Premium Compounder / AI Infrastructure",
        "sector": "Technology",
        "price": 155.00,
        "intrinsic_value": 165.00,
        "pe_ratio": 45,
        "fcf_yield": 2.0,
        "price_decline_pct": 8,
        "market_cap": 3800000000000,
        "quality": 98,
        "insider": 15,
        "macro": 88,
        "catalyst": 88,
        "risk": 45,
        "data_status": "fallback",
        "data_warnings": ["Live provider unavailable; using Catalyst fallback profile."],
        "reason": "Fallback profile: NVIDIA remains a premier AI infrastructure compounder, but valuation and concentration risk require discipline."
    }
}

def normalize_ticker(raw: str):
    t = raw.upper().strip()
    return TICKER_ALIASES.get(t, t)
