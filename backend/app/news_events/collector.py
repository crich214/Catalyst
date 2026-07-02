import re
import xml.etree.ElementTree as ET

import requests

from app.news_events.models import Event


RSS_SOURCES = [
    {
        "name": "Federal Reserve",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "category": "Monetary Policy",
    },
    {
        "name": "SEC",
        "url": "https://www.sec.gov/news/pressreleases.rss",
        "category": "Regulatory",
    },
    {
        "name": "USGS Earthquakes",
        "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom",
        "category": "Natural Event",
    },
]


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_magnitude(title):
    match = re.search(r"M\s?(\d+(\.\d+)?)", title)
    if not match:
        return None
    return float(match.group(1))


def fetch_rss_items(source):
    response = requests.get(
        source["url"],
        timeout=10,
        headers={"User-Agent": "CatalystEventEngine/0.1"},
    )
    response.raise_for_status()

    root = ET.fromstring(response.text)
    items = []

    for item in root.findall(".//item"):
        items.append({
            "title": clean_text(item.findtext("title") or "Untitled event"),
            "description": clean_text(item.findtext("description") or ""),
            "link": item.findtext("link") or source["url"],
            "source": source["name"],
            "category": source["category"],
        })

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = link_el.attrib.get("href") if link_el is not None else source["url"]

        items.append({
            "title": clean_text(entry.findtext("{http://www.w3.org/2005/Atom}title") or "Untitled event"),
            "description": clean_text(entry.findtext("{http://www.w3.org/2005/Atom}summary") or ""),
            "link": link,
            "source": source["name"],
            "category": source["category"],
        })

    return items


def event_from_item(item):
    text = f"{item['title']} {item['description']}".lower()

    importance = 45
    confidence = 70
    affected_sectors = []
    affected_companies = []
    bullish = False
    bearish = False
    time_horizon = "Short-term"

    if any(word in text for word in ["rate", "inflation", "fomc", "monetary", "fed"]):
        importance = 85
        affected_sectors = ["Banks", "REITs", "Homebuilders", "Utilities"]
        affected_companies = ["JPM", "BAC", "DHI", "LEN", "PLD"]
        bullish = True
        bearish = True
        time_horizon = "Medium-term"

    if item["source"] == "SEC":
        importance = 55
        affected_sectors = ["Financial Services", "Public Companies"]
        bullish = False
        bearish = False

        if any(word in text for word in ["fraud", "charges", "enforcement", "penalty", "settlement"]):
            importance = 80
            bearish = True

        if any(word in text for word in ["etf", "innovation", "comment", "market statistics", "ipo"]):
            importance = max(importance, 65)
            bullish = True

    if item["source"] == "USGS Earthquakes":
        magnitude = extract_magnitude(item["title"])
        importance = 35

        if magnitude:
            if magnitude >= 7:
                importance = 90
            elif magnitude >= 6:
                importance = 75
            elif magnitude >= 5:
                importance = 60
            else:
                importance = 40

        affected_sectors = ["Insurance", "Utilities", "Transportation"]

        if any(place in text for place in ["gulf", "texas", "louisiana", "refinery", "oil", "energy"]):
            affected_sectors.append("Energy")
            affected_companies = ["XOM", "CVX", "AIG", "DAL", "UAL"]
            importance = max(importance, 75)

        bullish = False
        bearish = importance >= 60

    summary = item["description"] or item["title"]

    return Event(
        title=item["title"],
        source=item["source"],
        category=item["category"],
        importance=importance,
        confidence=confidence,
        time_horizon=time_horizon,
        affected_sectors=affected_sectors,
        affected_companies=affected_companies,
        summary=summary[:350],
        bullish=bullish,
        bearish=bearish,
    )


def collect_live_events():
    events = []

    for source in RSS_SOURCES:
        try:
            items = fetch_rss_items(source)
            for item in items[:5]:
                events.append(event_from_item(item))
        except Exception:
            continue

    return events


def collect_sample_events():
    live_events = collect_live_events()

    if live_events:
        return live_events

    return [
        Event(
            title="No live event feeds available",
            source="Catalyst fallback",
            category="System",
            importance=20,
            confidence=50,
            time_horizon="Short-term",
            affected_sectors=[],
            affected_companies=[],
            summary="Catalyst could not reach live event feeds and is using fallback status.",
            bullish=False,
            bearish=False,
        )
    ]