"""Fetch feeds and build the digest text. Shared by the scheduled CLI and the interactive bot."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Mapping

from news_digest.digest import DEFAULT_MAX_STORIES, DEFAULT_WINDOW_HOURS, dedupe, format_digest, select_recent
from news_digest.feeds import Feed, Fetcher, fetch_all, http_get, load_feeds

log = logging.getLogger("news_digest")

DEFAULT_FEEDS_FILE = Path(__file__).resolve().parent.parent / "feeds.txt"


class AllFeedsFailed(Exception):
    """Every configured feed failed, so no digest can be built."""


@dataclass(frozen=True)
class DigestSettings:
    feeds: list[Feed]
    window_hours: float
    max_stories: int


def _env_number(env: Mapping[str, str], name: str, default: float, cast=float):
    raw = env.get(name, "").strip()
    return cast(raw) if raw else default


def load_settings(feeds_file: str | Path = DEFAULT_FEEDS_FILE, window_hours: float | None = None,
                  max_stories: int | None = None, env: Mapping[str, str] | None = None) -> DigestSettings:
    """Explicit arguments win over DIGEST_* / RSS_FEEDS environment variables.

    Raises ValueError (bad number, or no feeds configured) or OSError (feeds file unreadable).
    """
    env = os.environ if env is None else env
    window = window_hours or _env_number(env, "DIGEST_WINDOW_HOURS", DEFAULT_WINDOW_HOURS)
    limit = max_stories or _env_number(env, "DIGEST_MAX_STORIES", DEFAULT_MAX_STORIES, int)
    feeds = load_feeds(feeds_file, env)
    if not feeds:
        raise ValueError("No feeds configured (feeds.txt is empty and RSS_FEEDS is not set)")
    return DigestSettings(feeds=feeds, window_hours=window, max_stories=limit)


def build_digest(settings: DigestSettings, now: datetime, fetcher: Fetcher = http_get) -> str | None:
    """Return the digest text, or None when no story falls inside the time window.

    Raises AllFeedsFailed when not a single feed could be read.
    """
    feeds = settings.feeds
    stories, failures = fetch_all(feeds, fetcher)
    if len(failures) == len(feeds):
        raise AllFeedsFailed(
            f"All {len(feeds)} feeds failed; no digest was produced. Failures: "
            + "; ".join(f"{f.name}: {reason}" for f, reason in failures)
        )
    selected = select_recent(dedupe(stories), now, settings.window_hours, settings.max_stories)
    if not selected:
        log.info("No stories published in the last %gh across %d working feed(s).",
                 settings.window_hours, len(feeds) - len(failures))
        return None
    return format_digest(selected, now, settings.window_hours,
                         feeds_checked=len(feeds), feeds_failed=len(failures))
