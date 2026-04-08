#!/usr/bin/env python3
"""
Polymarket Trading Bot - Minimal FastAPI Web UI (paper mode only).

Routes:
  GET  /            -> dashboard HTML
  POST /run-cycle   -> run one cycle (paper mode only)
  GET  /api/status  -> latest cycle summary/status
"""
import logging
import os
import sys
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from app.bootstrap import build_orchestrator

# Ensure project root is on path when run directly
_project_root = Path(__file__).parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory state (reset on restart)
# ---------------------------------------------------------------------------
_last_outcome: dict[str, Any] | None = None
_recent_logs: deque[str] = deque(maxlen=50)


class _LogCaptureHandler(logging.Handler):
    """Append formatted log records to the in-memory deque."""

    def emit(self, record: logging.LogRecord) -> None:
        """Append a formatted log record to the shared in-memory log deque."""
        try:
            _recent_logs.append(self.format(record))
        except Exception as exc:  # noqa: BLE001
            # Swallow errors to avoid logging loops; print as last resort
            print(f"[_LogCaptureHandler] emit failed: {exc}", file=sys.stderr)


def _install_log_capture() -> None:
    handler = _LogCaptureHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logging.getLogger().addHandler(handler)


_install_log_capture()

# ---------------------------------------------------------------------------
# Safety helpers
# ---------------------------------------------------------------------------

def _is_real_trading_active() -> bool:
    """Return True if real trading is enabled via environment variable."""
    return os.environ.get("ENABLE_REAL_TRADING", "").lower() == "true"


def _get_execution_mode(config: dict) -> str:
    return config.get("execution_mode", "paper")


def _assert_paper_only(config: dict) -> None:
    """Raise HTTPException(403) if real trading is active or config mode is real."""
    if _is_real_trading_active():
        raise HTTPException(
            status_code=403,
            detail=(
                "Web UI refused: ENABLE_REAL_TRADING=true detected. "
                "The web UI operates in paper mode only."
            ),
        )
    mode = _get_execution_mode(config)
    if mode == "real":
        raise HTTPException(
            status_code=403,
            detail=(
                f"Web UI refused: execution_mode='{mode}'. "
                "The web UI operates in paper mode only."
            ),
        )


# ---------------------------------------------------------------------------
# Config / orchestrator helpers
# ---------------------------------------------------------------------------

def _get_profile() -> str:
    return os.environ.get("BOT_PROFILE", "paper_test")


def _get_config_dir() -> str:
    return os.environ.get("CONFIG_DIR", "config")


def _load_config() -> dict:
    from app.config.profile_manager import ProfileManager

    pm = ProfileManager(_get_config_dir())
    return pm.get_config(_get_profile())


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Polymarket Bot Web UI",
    description="Minimal dashboard for paper-mode trading cycles",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Polymarket Bot - Dashboard</title>
  <style>
    body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 1.5rem; }}
    h1   {{ color: #58a6ff; margin-bottom: 0.5rem; }}
    .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.85rem; margin-left: 0.5rem; }}
    .paper {{ background: #1f6feb; color: #fff; }}
    .real  {{ background: #da3633; color: #fff; }}
    .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1rem; margin: 1rem 0; }}
    .section h2 {{ color: #8b949e; font-size: 0.9rem; margin: 0 0 0.5rem 0; text-transform: uppercase; letter-spacing: 0.05em; }}
    table {{ border-collapse: collapse; width: 100%; }}
    td, th {{ text-align: left; padding: 0.3rem 0.6rem; border-bottom: 1px solid #21262d; }}
    th {{ color: #8b949e; font-size: 0.8rem; }}
    pre {{ background: #0d1117; padding: 0.5rem; overflow-x: auto; font-size: 0.8rem; max-height: 300px; overflow-y: auto; }}
    button {{
      background: #238636; color: #fff; border: none; padding: 0.5rem 1.2rem;
      border-radius: 6px; cursor: pointer; font-size: 1rem; margin-top: 0.5rem;
    }}
    button:hover {{ background: #2ea043; }}
    button:disabled {{ background: #444; cursor: not-allowed; }}
    #run-status {{ margin-top: 0.5rem; color: #8b949e; }}
    .ok      {{ color: #3fb950; }}
    .error   {{ color: #f85149; }}
    .skipped {{ color: #d29922; }}
  </style>
</head>
<body>
  <h1>Polymarket Bot
    <span class="badge {mode_class}">{mode}</span>
  </h1>

  <div class="section">
    <h2>Last Cycle</h2>
    <table>
      <tr><th>Cycle ID</th><td>{cycle_id}</td></tr>
      <tr><th>Status</th><td class="{status_class}">{status}</td></tr>
      <tr><th>Started</th><td>{started_at}</td></tr>
      <tr><th>Finished</th><td>{finished_at}</td></tr>
      <tr><th>Markets Scanned</th><td>{markets_scanned}</td></tr>
      <tr><th>Signals Generated</th><td>{signals_generated}</td></tr>
      <tr><th>Trades Attempted</th><td>{trades_attempted}</td></tr>
      <tr><th>Trades Executed</th><td>{trades_executed}</td></tr>
      <tr><th>Error</th><td class="error">{error}</td></tr>
    </table>
  </div>

  <div class="section">
    <h2>Run One Cycle</h2>
    <button id="run-btn" onclick="runCycle()">▶ Run Cycle</button>
    <div id="run-status"></div>
  </div>

  <div class="section">
    <h2>Recent Logs (last 50 lines)</h2>
    <pre id="log-output">{recent_logs}</pre>
  </div>

  <script>
    async function runCycle() {{
      const btn = document.getElementById('run-btn');
      const status = document.getElementById('run-status');
      btn.disabled = true;
      status.textContent = 'Running…';
      try {{
        const resp = await fetch('/run-cycle', {{ method: 'POST' }});
        const data = await resp.json();
        if (resp.ok) {{
          status.textContent = '✓ Done: ' + JSON.stringify(data);
        }} else {{
          status.textContent = '✗ Error: ' + (data.detail || JSON.stringify(data));
        }}
      }} catch(e) {{
        status.textContent = '✗ Network error: ' + e.message;
      }} finally {{
        btn.disabled = false;
        setTimeout(() => location.reload(), 1500);
      }}
    }}
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, summary="Dashboard")
async def dashboard() -> HTMLResponse:
    """Render the bot dashboard."""
    config = _load_config()
    mode = _get_execution_mode(config)
    mode_class = "paper" if mode != "real" else "real"

    if _last_outcome:
        o = _last_outcome
        cycle_id = o.get("cycle_id", "-")
        status = o.get("status", "-")
        started_at = o.get("started_at", "-")
        finished_at = o.get("finished_at", "-")
        markets_scanned = o.get("markets_scanned", 0)
        signals_generated = o.get("signals_generated", 0)
        trades_attempted = o.get("trades_attempted", 0)
        trades_executed = o.get("trades_executed", 0)
        error = o.get("error") or ""
    else:
        cycle_id = status = started_at = finished_at = "-"
        markets_scanned = signals_generated = trades_attempted = trades_executed = 0
        error = ""

    status_class = {"ok": "ok", "error": "error", "skipped": "skipped"}.get(
        str(status).lower(), ""
    )

    logs_text = "\n".join(_recent_logs) if _recent_logs else "(no logs yet)"

    html = _DASHBOARD_HTML.format(
        mode=mode,
        mode_class=mode_class,
        cycle_id=cycle_id,
        status=status,
        status_class=status_class,
        started_at=started_at,
        finished_at=finished_at,
        markets_scanned=markets_scanned,
        signals_generated=signals_generated,
        trades_attempted=trades_attempted,
        trades_executed=trades_executed,
        error=error,
        recent_logs=logs_text,
    )
    return HTMLResponse(content=html)


@app.post("/run-cycle", summary="Run one trading cycle (paper only)")
async def run_cycle() -> JSONResponse:
    """Execute one trading cycle.  Refuses if real trading is active."""
    global _last_outcome

    config = _load_config()
    _assert_paper_only(config)

    orchestrator = build_orchestrator(config)
    outcome = orchestrator.run_cycle()

    _last_outcome = {
        "cycle_id": outcome.cycle_id,
        "status": outcome.status.value,
        "started_at": outcome.started_at,
        "finished_at": outcome.finished_at,
        "markets_scanned": outcome.markets_scanned,
        "signals_generated": outcome.signals_generated,
        "trades_attempted": outcome.trades_attempted,
        "trades_executed": outcome.trades_executed,
        "error": outcome.error,
    }

    return JSONResponse(content=_last_outcome, status_code=200)


@app.get("/api/status", summary="Latest cycle status")
async def api_status() -> JSONResponse:
    """Return the latest cycle outcome as JSON, or a 'no cycles yet' message."""
    config = _load_config()
    mode = _get_execution_mode(config)
    real_trading = _is_real_trading_active()

    payload: dict[str, Any] = {
        "mode": mode,
        "real_trading_enabled": real_trading,
        "last_cycle": _last_outcome,
    }
    return JSONResponse(content=payload)


# ---------------------------------------------------------------------------
# Entrypoint (run with: python web_app.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    # Change to project root so relative config/log paths resolve
    os.chdir(_project_root)

    uvicorn.run(
        "web_app:app",
        host=os.environ.get("WEB_HOST", "127.0.0.1"),
        port=int(os.environ.get("WEB_PORT", "8000")),
        reload=False,
        log_level=os.environ.get("LOG_LEVEL", "info").lower(),
    )
