import os

TARGET_MARKETS = [
    {"name": "BTC Up/Down 5m",  "market_id": "1903731"},
    {"name": "BTC Up/Down 15m", "market_id": "1903701"},
    {"name": "BTC Up/Down 1h",  "market_id": "1887954"},
]

def _ids_from_env() -> set[str]:
    raw = os.getenv("TARGET_MARKET_IDS", "").strip()
    if not raw:
        return {m["market_id"] for m in TARGET_MARKETS}
    return {x.strip() for x in raw.split(",") if x.strip()}

TARGET_MARKET_IDS = _ids_from_env()

def is_target_market(m: dict) -> bool:
    mid = str(m.get("id") or m.get("market_id") or "")
    return mid in TARGET_MARKET_IDS

def market_display_name(m: dict) -> str:
    mid = str(m.get("id") or m.get("market_id") or "")
    if mid == "1903731":
        return "BTC Up/Down 5m"
    if mid == "1903701":
        return "BTC Up/Down 15m"
    if mid == "1887954":
        return "BTC Up/Down 1h"
    return str(m.get("slug") or m.get("question") or mid or "Unknown BTC Market")
