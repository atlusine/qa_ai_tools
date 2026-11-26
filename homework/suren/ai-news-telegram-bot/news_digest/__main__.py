"""Build the AI news digest and send it to Telegram (or print it with --preview).

    python -m news_digest --preview      # print only; no Telegram credentials needed
    python -m news_digest                # send to TELEGRAM_CHAT_ID

Exit codes: 0 sent / previewed / skipped (no recent stories),
            1 Telegram delivery error, 2 all feeds failed, 3 configuration error.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone

from news_digest.build import DEFAULT_FEEDS_FILE, AllFeedsFailed, build_digest, load_settings
from news_digest.digest import DEFAULT_MAX_STORIES, DEFAULT_WINDOW_HOURS
from news_digest.feeds import Fetcher, http_get
from notifier.config import ensure_utf8_output, load_dotenv
from notifier.telegram import EXIT_CONFIG_ERROR, deliver

log = logging.getLogger("news_digest")

EXIT_ALL_FEEDS_FAILED = 2

__all__ = ["DEFAULT_FEEDS_FILE", "EXIT_ALL_FEEDS_FAILED", "main", "run"]


def run(argv: list[str] | None = None, *, now: datetime | None = None, fetcher: Fetcher = http_get) -> int:
    parser = argparse.ArgumentParser(prog="python -m news_digest", description="Send a daily AI news digest to Telegram.")
    parser.add_argument("--preview", action="store_true", help="print the message; do not call Telegram")
    parser.add_argument("--feeds-file", default=str(DEFAULT_FEEDS_FILE), help="feed list file (default: feeds.txt)")
    parser.add_argument("--window-hours", type=float, help=f"time window (env DIGEST_WINDOW_HOURS, default {DEFAULT_WINDOW_HOURS})")
    parser.add_argument("--max-stories", type=int, help=f"maximum stories (env DIGEST_MAX_STORIES, default {DEFAULT_MAX_STORIES})")
    args = parser.parse_args(argv)

    load_dotenv()
    try:
        settings = load_settings(args.feeds_file, args.window_hours, args.max_stories)
    except (ValueError, OSError) as exc:
        log.error("Invalid configuration: %s", exc)
        return EXIT_CONFIG_ERROR

    now = now or datetime.now(timezone.utc)
    try:
        text = build_digest(settings, now, fetcher)
    except AllFeedsFailed as exc:
        log.error("%s", exc)
        return EXIT_ALL_FEEDS_FAILED
    if text is None:
        log.info("Nothing new in the last %gh; skipping send.", settings.window_hours)
        return 0

    code = deliver(text, args.preview)
    if code == 0 and not args.preview:
        log.info("Digest sent to Telegram")
    return code


def main() -> int:
    ensure_utf8_output()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    return run()


if __name__ == "__main__":
    sys.exit(main())
