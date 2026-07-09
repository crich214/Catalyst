from typing import List
import requests

from app.information.classifier import (
    determine_direction,
    determine_event_type,
    determine_materiality,
)
from app.information.domain_router import determine_domains
from app.information.models import InformationItem


SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

HEADERS = {
    "User-Agent": "Catalyst Investment Intelligence contact@example.com"
}


def get_sec_filings(ticker: str) -> List[InformationItem]:
    items: List[InformationItem] = []

    cik = lookup_cik(ticker)

    if not cik:
        return items

    try:
        url = SEC_SUBMISSIONS_URL.format(cik=cik)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return items

    filings = data.get("filings", {}).get("recent", {})

    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accession_numbers = filings.get("accessionNumber", [])
    primary_documents = filings.get("primaryDocument", [])

    for index, form in enumerate(forms[:10]):
        if form not in ["8-K", "10-Q", "10-K", "DEF 14A", "4"]:
            continue

        filing_date = safe_get(dates, index)
        accession = safe_get(accession_numbers, index)
        document = safe_get(primary_documents, index)

        title = f"{ticker.upper()} filed {form}"
        summary = build_summary(ticker, form, filing_date)

        event_type = determine_sec_event_type(form)
        materiality = determine_sec_materiality(form)
        direction = determine_direction(title, summary)

        items.append(
            InformationItem(
                title=title,
                source="SEC EDGAR",
                category="SEC Filing",
                ticker=ticker.upper(),
                summary=summary,
                materiality=materiality,
                direction=direction,
                confidence=95,
                affected_domains=determine_domains(event_type),
                url=build_sec_url(cik, accession, document),
                event_type=event_type,
            )
        )

    return items


def lookup_cik(ticker: str) -> str:
    try:
        response = requests.get(SEC_TICKERS_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return ""

    target = ticker.upper()

    for company in data.values():
        if company.get("ticker", "").upper() == target:
            cik = str(company.get("cik_str", "")).zfill(10)
            return cik

    return ""


def determine_sec_event_type(form: str) -> str:
    if form == "8-K":
        return "RegulatoryRisk"

    if form in ["10-Q", "10-K"]:
        return "Earnings"

    if form == "DEF 14A":
        return "Governance"

    if form == "4":
        return "InsiderActivity"

    return "General"


def determine_sec_materiality(form: str) -> str:
    if form == "8-K":
        return "High"

    if form in ["10-Q", "10-K"]:
        return "Medium"

    if form in ["DEF 14A", "4"]:
        return "Medium"

    return "Low"


def build_summary(ticker: str, form: str, filing_date: str) -> str:
    descriptions = {
        "8-K": "material current report",
        "10-Q": "quarterly report",
        "10-K": "annual report",
        "DEF 14A": "proxy statement",
        "4": "insider transaction filing",
    }

    description = descriptions.get(form, "SEC filing")

    return (
        f"{ticker.upper()} filed a {description}"
        f"{f' on {filing_date}' if filing_date else ''}."
    )


def build_sec_url(cik: str, accession: str, document: str):
    if not cik or not accession or not document:
        return None

    accession_clean = accession.replace("-", "")
    cik_clean = str(int(cik))

    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_clean}/{accession_clean}/{document}"
    )


def safe_get(values, index):
    try:
        return values[index]
    except Exception:
        return ""