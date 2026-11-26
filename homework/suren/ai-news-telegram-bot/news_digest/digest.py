"""Duplicate removal, recency selection and message formatting."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from news_digest.feeds import Story

DEFAULT_WINDOW_HOURS = 24
DEFAULT_MAX_STORIES = 5
# Allow a little clock skew, but ignore items dated far in the future (broken feeds).
FUTURE_TOLERANCE = timedelta(hours=1)

_TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src", "cmpid", "taid", "guccounter"}


def normalize_link(url: str) -> str:
    parts = urlparse(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_PARAMS]
    path = parts.path.rstrip("/") or "/"
    return urlunparse(("https", host, path, "", urlencode(sorted(query)), ""))


def normalize_title(title: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", title.casefold()).split())


def dedupe(stories: list[Story]) -> list[Story]:
    """Drop stories whose normalized link OR normalized title was already seen.

    Stories are processed newest first, so the most recent copy is kept.
    """
    seen_links: set[str] = set()
    seen_titles: set[str] = set()
    unique = []
    for story in sorted(stories, key=lambda s: s.published, reverse=True):
        link, title = normalize_link(story.link), normalize_title(story.title)
        if link in seen_links or title in seen_titles:
            continue
        seen_links.add(link)
        seen_titles.add(title)
        unique.append(story)
    return unique


def select_recent(stories: list[Story], now: datetime, window_hours: float = DEFAULT_WINDOW_HOURS,
                  limit: int = DEFAULT_MAX_STORIES) -> list[Story]:
    """Newest-first stories published within the last `window_hours`, at most `limit`."""
    cutoff = now - timedelta(hours=window_hours)
    recent = [s for s in stories if cutoff <= s.published <= now + FUTURE_TOLERANCE]
    return sorted(recent, key=lambda s: s.published, reverse=True)[:limit]


def _hours(value: float) -> str:
    return f"{value:g}h"


def format_digest(stories: list[Story], now: datetime, window_hours: float,
                  feeds_checked: int, feeds_failed: int) -> str:
    lines = [f"🤖 AI News Digest — {now:%d %b %Y}", ""]
    for number, story in enumerate(stories, start=1):
        lines.append(f"{number}. {story.title}")
        lines.append(f"   Source: {story.source} · {story.published:%d %b %H:%M} UTC")
        lines.append(f"   {story.link}")
        lines.append("")
    footer = f"Top {len(stories)} stories from the last {_hours(window_hours)} · {feeds_checked} feeds checked"
    if feeds_failed:
        footer += f" ({feeds_failed} unavailable)"
    lines.append(footer)
    return "\n".join(lines)
