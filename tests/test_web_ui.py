"""Smoke tests for the FastAPI Web UI (paper mode only)."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_outcome():
    """Return a mock CycleOutcome for paper mode."""
    from app.orchestration.cycle_outcome import CycleOutcome
    from app.shared.enums import CycleStatus
    from app.shared.time_utils import utcnow_iso

    return CycleOutcome(
        cycle_id="test-cycle-1",
        status=CycleStatus.OK,
        started_at=utcnow_iso(),
        finished_at=utcnow_iso(),
        markets_scanned=3,
        signals_generated=1,
        trades_attempted=1,
        trades_executed=1,
        found_signals=[
            {
                "signal_id": "sig-1",
                "market_id": "mkt-a",
                "module": "edge_estimator",
                "score": 0.75,
                "side": "yes",
                "confidence": 0.8,
                "metadata": {"edge": 0.05},
            }
        ],
    )


def _make_client():
    """Reset the app's in-memory state for test isolation."""
    import web_app
    web_app._last_outcome = None
    web_app._recent_logs.clear()


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_dashboard_returns_html():
    """GET / must return 200 with HTML content."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Polymarket Bot" in resp.text


@pytest.mark.anyio
async def test_dashboard_shows_no_cycle_placeholder():
    """Dashboard renders '-' placeholders when no cycle has run yet."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200


@pytest.mark.anyio
async def test_dashboard_shows_last_outcome_after_cycle():
    """Dashboard displays last cycle data once a cycle has completed."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-abc",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 5,
        "signals_generated": 2,
        "trades_attempted": 1,
        "trades_executed": 1,
        "error": None,
    }

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "cycle-abc" in resp.text


# ---------------------------------------------------------------------------
# POST /run-cycle
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_run_cycle_paper_mode_success():
    """POST /run-cycle succeeds in paper mode and returns cycle data."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    mock_outcome = _make_mock_outcome()
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_cycle.return_value = mock_outcome

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch("web_app.build_orchestrator", return_value=mock_orchestrator),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.post("/run-cycle")

    assert resp.status_code == 200
    data = resp.json()
    assert data["cycle_id"] == "test-cycle-1"
    assert data["status"] == "ok"
    assert data["markets_scanned"] == 3
    assert data["trades_executed"] == 1


@pytest.mark.anyio
async def test_run_cycle_updates_last_outcome():
    """POST /run-cycle updates the in-memory _last_outcome."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    mock_outcome = _make_mock_outcome()
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_cycle.return_value = mock_outcome

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch("web_app.build_orchestrator", return_value=mock_orchestrator),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            await client.post("/run-cycle")

    assert web_app._last_outcome is not None
    assert web_app._last_outcome["cycle_id"] == "test-cycle-1"


@pytest.mark.anyio
async def test_run_cycle_refused_when_real_trading_env():
    """POST /run-cycle must return 403 when ENABLE_REAL_TRADING=true."""
    from httpx import ASGITransport, AsyncClient
    import web_app

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "true"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.post("/run-cycle")

    assert resp.status_code == 403
    assert "paper mode" in resp.json()["detail"].lower()


@pytest.mark.anyio
async def test_run_cycle_refused_when_mode_is_real():
    """POST /run-cycle must return 403 when execution_mode=real in config."""
    from httpx import ASGITransport, AsyncClient
    import web_app

    with (
        patch("web_app._load_config", return_value={"execution_mode": "real"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.post("/run-cycle")

    assert resp.status_code == 403
    assert "paper mode" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# GET /api/status
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_api_status_no_cycle_yet():
    """GET /api/status returns null last_cycle before any cycle has run."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/status")

    assert resp.status_code == 200
    data = resp.json()
    assert data["last_cycle"] is None
    assert data["mode"] == "paper"
    assert data["real_trading_enabled"] is False


@pytest.mark.anyio
async def test_api_status_returns_last_cycle():
    """GET /api/status returns last cycle data after a cycle."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-xyz",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 2,
        "signals_generated": 0,
        "trades_attempted": 0,
        "trades_executed": 0,
        "error": None,
    }

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/status")

    assert resp.status_code == 200
    data = resp.json()
    assert data["last_cycle"]["cycle_id"] == "cycle-xyz"
    assert data["last_cycle"]["status"] == "ok"


@pytest.mark.anyio
async def test_api_status_reflects_real_trading_flag():
    """GET /api/status correctly reports real_trading_enabled."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "true"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/status")

    assert resp.status_code == 200
    data = resp.json()
    assert data["real_trading_enabled"] is True


# ---------------------------------------------------------------------------
# Found Signals in API /api/status
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_api_status_includes_found_signals():
    """GET /api/status returns found_signals list in last_cycle."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-sig",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 2,
        "signals_generated": 1,
        "trades_attempted": 1,
        "trades_executed": 1,
        "error": None,
        "found_signals": [
            {
                "signal_id": "sig-99",
                "market_id": "mkt-z",
                "module": "book_imbalance",
                "score": 0.6,
                "side": "no",
                "confidence": 0.7,
                "metadata": {},
            }
        ],
    }

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/status")

    assert resp.status_code == 200
    data = resp.json()
    assert "found_signals" in data["last_cycle"]
    signals = data["last_cycle"]["found_signals"]
    assert isinstance(signals, list)
    assert len(signals) == 1
    assert signals[0]["signal_id"] == "sig-99"
    assert signals[0]["module"] == "book_imbalance"


@pytest.mark.anyio
async def test_api_status_empty_found_signals():
    """GET /api/status returns empty list when no signals were found."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-empty",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 1,
        "signals_generated": 0,
        "trades_attempted": 0,
        "trades_executed": 0,
        "error": None,
        "found_signals": [],
    }

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/status")

    assert resp.status_code == 200
    data = resp.json()
    assert data["last_cycle"]["found_signals"] == []


# ---------------------------------------------------------------------------
# Found Signals rendered in dashboard GET /
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_dashboard_shows_found_signals_section():
    """Dashboard HTML includes a 'Found Signals' section."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "Found Signals" in resp.text


@pytest.mark.anyio
async def test_dashboard_renders_signal_data():
    """Dashboard shows signal details when last cycle has found signals."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-render",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 3,
        "signals_generated": 1,
        "trades_attempted": 1,
        "trades_executed": 1,
        "error": None,
        "found_signals": [
            {
                "signal_id": "sig-render",
                "market_id": "mkt-render",
                "module": "spread_pressure",
                "score": 0.9,
                "side": "yes",
                "confidence": 0.95,
                "metadata": {"spread": 0.02},
            }
        ],
    }

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "sig-render" in resp.text
    assert "mkt-render" in resp.text
    assert "spread_pressure" in resp.text


@pytest.mark.anyio
async def test_dashboard_no_signals_placeholder():
    """Dashboard shows placeholder text when no signals exist."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = {
        "cycle_id": "cycle-nosig",
        "status": "ok",
        "started_at": "2024-01-01T00:00:00Z",
        "finished_at": "2024-01-01T00:00:01Z",
        "markets_scanned": 1,
        "signals_generated": 0,
        "trades_attempted": 0,
        "trades_executed": 0,
        "error": None,
        "found_signals": [],
    }

    async with AsyncClient(
        transport=ASGITransport(app=web_app.app), base_url="http://test"
    ) as client:
        resp = await client.get("/")

    assert resp.status_code == 200
    assert "no signals found" in resp.text


@pytest.mark.anyio
async def test_run_cycle_response_includes_found_signals():
    """POST /run-cycle response includes found_signals list."""
    from httpx import ASGITransport, AsyncClient
    import web_app
    web_app._last_outcome = None

    mock_outcome = _make_mock_outcome()
    mock_orchestrator = MagicMock()
    mock_orchestrator.run_cycle.return_value = mock_outcome

    with (
        patch("web_app._load_config", return_value={"execution_mode": "paper"}),
        patch("web_app.build_orchestrator", return_value=mock_orchestrator),
        patch.dict(os.environ, {"ENABLE_REAL_TRADING": "false"}),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=web_app.app), base_url="http://test"
        ) as client:
            resp = await client.post("/run-cycle")

    assert resp.status_code == 200
    data = resp.json()
    assert "found_signals" in data
    assert isinstance(data["found_signals"], list)
    assert len(data["found_signals"]) == 1
    assert data["found_signals"][0]["signal_id"] == "sig-1"
