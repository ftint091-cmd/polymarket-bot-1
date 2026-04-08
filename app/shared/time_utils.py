from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def utcnow_iso() -> str:
    return utcnow().isoformat()

def ts_ms() -> int:
    return int(utcnow().timestamp() * 1000)
