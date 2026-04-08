#!/usr/bin/env python3
"""
Polymarket Trading Bot - Main entrypoint.
Bootstrap only. No business logic here.
"""
import logging
import os
import sys
from pathlib import Path

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

def main() -> None:
    setup_logging(os.environ.get("LOG_LEVEL", "INFO"))
    logger = logging.getLogger(__name__)

    # Ensure working directory is project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    profile = os.environ.get("BOT_PROFILE", "default")
    config_dir = os.environ.get("CONFIG_DIR", "config")

    logger.info("Starting Polymarket Trading Bot (profile=%s)", profile)

    from app.bootstrap import build_controller
    from app.controller.command_model import Command
    from app.shared.enums import CommandType

    controller = build_controller(profile=profile, config_dir=config_dir)

    # Start the bot
    result = controller.execute(Command(type=CommandType.START))
    if not result.success:
        logger.error("Failed to start: %s", result.message)
        sys.exit(1)

    logger.info("Bot running. Press Ctrl+C to stop.")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        controller.execute(Command(type=CommandType.STOP))
        logger.info("Bot stopped.")

if __name__ == "__main__":
    main()
