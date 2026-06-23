from __future__ import annotations

import logging
from pathlib import Path

from settings.config import AppConfig
from utils.logging_config import configure_logging


def main() -> None:
    """Application entry point."""
    config = AppConfig.load()
    configure_logging(config.log_file)
    logging.getLogger(__name__).info("Starting Mynoh")
    try:
        from ui.app import run_app
    except Exception as exc:  # pragma: no cover - environment/import guard
        logging.exception("Could not start UI: %s", exc)
        raise SystemExit("Flet is required to launch the desktop UI. Run: pip install -e .") from exc
    run_app(config)


if __name__ == "__main__":
    main()
