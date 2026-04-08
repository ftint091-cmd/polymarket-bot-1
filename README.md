# Polymarket Trading Bot V1

Automated trading bot for [Polymarket](https://polymarket.com) prediction markets, built with a strict layered architecture.

> ⚠️ **WARNING**: Real trading mode involves financial risk. Default mode is **paper trading** (simulation only).

## Architecture

```
main → controller → orchestrator → [monitor → state_builder → analytics → decision → sizing → risk → execution → positions → observability]
```

### Layer Responsibilities

| Layer | Responsibility |
|-------|---------------|
| `controller` | Lifecycle management (start/stop/pause), command routing, fault escalation |
| `orchestrator` | Fixed pipeline execution, cycle outcome collection |
| `market/monitor` | Collects raw market data from Polymarket + Binance |
| `state` | Single immutable CycleState built per cycle |
| `analytics` | Runs enabled analysis modules, generates signals with signal_id |
| `decision` | Gate + confidence + response mode → trade yes/no decision |
| `sizing` | Calculates recommended position size |
| `risk` | Capital/exposure validation, can cut or reject size |
| `execution` | Routes to paper/fake_real/real executor |
| `positions` | Source of truth for live positions |
| `observability` | Separate loggers for cycle/signal/execution/command/events |

## Quick Start

### Prerequisites
- Python 3.11+

### Installation

```bash
# Clone and set up
git clone https://github.com/ftint091-cmd/polymarket-bot-1
cd polymarket-bot-1

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
```

### Run in Paper Mode (Safe)

```bash
# Single cycle smoke test
python run_single_cycle.py

# Run continuously
python main.py
```

### Web UI (Paper Mode Only)

A minimal FastAPI dashboard lets you trigger and inspect trading cycles from a browser.

```bash
# Install web dependencies (FastAPI + Uvicorn)
pip install -r requirements.txt

# Start the web UI (paper mode is the default)
python web_app.py

# Or with uvicorn directly:
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

**Available routes:**

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Dashboard HTML: mode, last cycle stats, recent logs |
| `/run-cycle` | POST | Execute one cycle (paper mode only) |
| `/api/status` | GET | Latest cycle summary as JSON |

> ⛔ **Safety**: The web UI will return `403 Forbidden` if `ENABLE_REAL_TRADING=true`
> or if `execution_mode` is set to `real`. It operates in **paper mode only**.

Optional environment variables for the web UI:

| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_PORT` | `8000` | Port to listen on |
| `WEB_HOST` | `127.0.0.1` | Host to bind to (`0.0.0.0` exposes to all interfaces) |
| `BOT_PROFILE` | `paper_test` | Config profile |
| `CONFIG_DIR` | `config` | Path to config directory |

### Run with a specific profile

```bash
BOT_PROFILE=cautious python main.py
BOT_PROFILE=aggressive python main.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_PROFILE` | `default` | Config profile to use |
| `BOT_EXECUTION_MODE` | `paper` | `paper`, `fake_real`, or `real` |
| `ENABLE_REAL_TRADING` | `false` | Must be `true` for real mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CONFIG_DIR` | `config` | Path to config directory |
| `POLYMARKET_API_KEY` | - | Required for real mode |
| `POLYMARKET_API_SECRET` | - | Required for real mode |
| `BINANCE_API_KEY` | - | Optional, for reference data |

## Config Profiles

| Profile | Description |
|---------|-------------|
| `default` | Balanced settings |
| `cautious` | Small sizes, high confidence threshold |
| `aggressive` | Larger sizes, lower confidence threshold |
| `paper_test` | For CI/smoke testing, fast cycles |

## Running Tests

```bash
pytest tests/ -v
```

## ⚠️ Real Mode Warning

Real trading mode:
1. Requires `ENABLE_REAL_TRADING=true` environment variable
2. Requires valid Polymarket API credentials
3. **Will place real orders with real money**
4. Is **disabled by default** and requires explicit opt-in

Never set `ENABLE_REAL_TRADING=true` unless you understand the risks and have tested thoroughly in paper mode.

## Project Structure

```
app/
├── controller/     # Lifecycle, commands, fault policy
├── orchestration/  # Pipeline coordinator
├── config/         # Config loading, merging, validation
├── infrastructure/ # API clients, HTTP transport, secrets
├── market/         # Market monitor + adapters
├── state/          # CycleState schema + builder
├── analytics/      # Analysis modules + filters
├── decision/       # Gate + confidence + decision
├── sizing/         # Position sizing
├── risk/           # Capital + exposure checks
├── execution/      # Paper/fake_real/real executors
├── positions/      # Position store + service
├── observability/  # Loggers + performance stats
└── shared/         # Enums, IDs, exceptions, utils
```

## License

Private - All rights reserved.