TARGET_MARKETS = [
    {"name": "BTC Up/Down 5m",  "slug_hint": "btc-updown-5m"},
    {"name": "BTC Up/Down 15m", "slug_hint": "btc-updown-15m"},
    {"name": "BTC Up/Down 1h",  "slug_hint": "bitcoin-up-or-down"},
]

def is_target_market(m: dict) -> bool:
    text = " ".join([
        str(m.get("slug", "")),
        str(m.get("question", "")),
        str(m.get("title", "")),
        str(m.get("name", "")),
    ]).lower()

    if not ("btc" in text or "bitcoin" in text):
        return False

    is_5m = ("5m" in text) or ("5 min" in text) or ("5 minute" in text)
    is_15m = ("15m" in text) or ("15 min" in text) or ("15 minute" in text)
    is_1h = ("1h" in text) or ("1 hour" in text) or ("hour" in text)

    return is_5m or is_15m or is_1h

def market_display_name(m: dict) -> str:
    text = " ".join([
        str(m.get("slug", "")),
        str(m.get("question", "")),
        str(m.get("title", "")),
        str(m.get("name", "")),
    ]).lower()

    if "15m" in text or "15 min" in text or "15 minute" in text:
        return "BTC Up/Down 15m"
    if "5m" in text or "5 min" in text or "5 minute" in text:
        return "BTC Up/Down 5m"
    if "1h" in text or "1 hour" in text or "hour" in text:
        return "BTC Up/Down 1h"
    return str(m.get("slug") or m.get("market_id") or "Unknown BTC Market")
