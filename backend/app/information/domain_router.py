def determine_domains(event_type: str):
    routing = {
        "StrategicTransaction": ["Business", "Risk", "Portfolio"],
        "Earnings": ["Business", "Portfolio"],
        "RegulatoryRisk": ["Risk"],
        "Governance": ["Business", "Risk"],
        "InsiderActivity": ["Business", "Portfolio"],
        "Macro": ["Macro", "Portfolio"],
        "Geopolitical": ["Macro", "Risk"],
        "General": ["Business", "Risk", "Portfolio"],
    }

    return routing.get(event_type, ["Business", "Risk", "Portfolio"])