"""Run the interactive digest bot until stopped (Ctrl+C).

    python -m bot                       # logs to the console
    python -m bot --log-file bot.log    # also logs to a rotating file (used by the Windows autostart task)

Needs only TELEGRAM_BOT_TOKEN (from .env in the current directory or the environment).
Exit codes: 0 stopped with Ctrl+C, 3 configuration error (missing or rejected token).
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from logging.handlers import RotatingFileHandler

from bot.app import DigestBot, make_builder
from notifier.config import ConfigError, ensure_utf8_output, get_bot_token, load_dotenv
from notifier.telegram import EXIT_CONFIG_ERROR, TelegramError

log = logging.getLogger("bot")


def _configure_logging(log_file: str | None) -> None:
    handlers: list[logging.Handler] = []
    if sys.stderr is not None:  # None under pythonw.exe (no console)
        handlers.append(logging.StreamHandler())
    if log_file:
        handlers.append(RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=handlers)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bot", description="Telegram bot that sends the AI news digest on demand.")
    parser.add_argument("--log-file", help="also write logs to this file (rotated at 1 MB)")
    args = parser.parse_args(argv)

    ensure_utf8_output()
    _configure_logging(args.log_file)
    load_dotenv()
    try:
        token = get_bot_token()
    except ConfigError as exc:
        log.error("%s", exc)
        return EXIT_CONFIG_ERROR

    bot = DigestBot(token, make_builder())
    delay = 5
    while True:  # at boot the network may not be up yet, so keep retrying
        try:
            username = bot.setup()
            break
        except TelegramError as exc:
            if "401" in str(exc) or "404" in str(exc):
                log.error("Telegram rejected the bot token: %s", exc)
                return EXIT_CONFIG_ERROR
            log.warning("Telegram not reachable yet (%s); retrying in %ds", exc, delay)
            time.sleep(delay)
            delay = min(60, delay * 2)

    log.info("Bot @%s is running. Open it in Telegram and press /start. Ctrl+C to stop.", username)
    try:
        bot.run_forever()
    except KeyboardInterrupt:
        log.info("Stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
