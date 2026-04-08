# Polymarket Trading Bot

Automated trading bot for Polymarket prediction markets.

## Architecture V1

This bot implements a full trading pipeline:

```
main → controller → orchestrator → monitor → state_builder → analytics → decision → sizing → risk → execution → positions → observability
```

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Configure profiles in `config/profiles/`
4. Run: `python main.py`

## License

Private - All rights reserved.