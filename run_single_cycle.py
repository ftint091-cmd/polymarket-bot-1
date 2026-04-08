#!/usr/bin/env python3
"""
Run a single trading cycle for smoke testing and debugging.
Uses the same orchestrator contract as main.py.
"""
import logging
import os
import sys
from pathlib import Path

def setup_logging(level: str = "DEBUG") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.DEBUG),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

def main() -> None:
    setup_logging(os.environ.get("LOG_LEVEL", "DEBUG"))
    logger = logging.getLogger(__name__)

    project_root = Path(__file__).parent
    os.chdir(project_root)

    profile = os.environ.get("BOT_PROFILE", "paper_test")
    config_dir = os.environ.get("CONFIG_DIR", "config")

    logger.info("=== Single Cycle Run (profile=%s) ===", profile)

    from app.config.profile_manager import ProfileManager
    from app.bootstrap import build_orchestrator

    profile_manager = ProfileManager(config_dir)
    config = profile_manager.get_config(profile)

    logger.info("Execution mode: %s", config.get("execution_mode"))

    orchestrator = build_orchestrator(config)
    outcome = orchestrator.run_cycle()

    logger.info("=== Cycle Complete ===")
    logger.info("  cycle_id:         %s", outcome.cycle_id)
    logger.info("  status:           %s", outcome.status.value)
    logger.info("  markets_scanned:  %d", outcome.markets_scanned)
    logger.info("  signals_generated:%d", outcome.signals_generated)
    logger.info("  trades_attempted: %d", outcome.trades_attempted)
    logger.info("  trades_executed:  %d", outcome.trades_executed)
    if outcome.error:
        logger.error("  error:            %s", outcome.error)
        sys.exit(1)

    logger.info("=== Success ===")

if __name__ == "__main__":
    main()
