"""Load the feed list and fetch stories. One failing feed never stops the others."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import feedparser

log = logging.getLogger("news_digest.feeds")

USER_AGENT = "ai-news-digest/1.0 (+https://github.com; RSS reader)"
Fetcher = Callable[[str], bytes]


@dataclass(frozen=True)
class Feed:
    name: str
    url: str


@dataclass(frozen=True)
class Story:
    title: str
    link: str
    source: str
    published: datetime  # timezone-aware, UTC


class FeedError(Exception):
    pass


def parse_feed_list(text: str) -> list[Feed]:
    feeds = []
    # Drop comment lines first, then allow ";" as an extra separator (handy for RSS_FEEDS).
    entries = [part for line in text.splitlines() if not line.strip().startswith("#") for part in line.split(";")]
    for raw in entries:
        line = raw.strip()
        if not line:
            continue
        if "|" in line:
            name, _, url = (part.strip() for part in line.partition("|"))
        else:
            name, url = "", line
        feeds.append(Feed(name=name or urlparse(url).netloc, url=url))
    return feeds


def load_feeds(path: str | Path, env: Mapping[str, str]) -> list[Feed]:
    """RSS_FEEDS (env) overrides the feeds file."""
    override = env.get("RSS_FEEDS", "").strip()
    if override:
        return parse_feed_list(override)
    return parse_feed_list(Path(path).read_text(encoding="utf-8"))


def http_get(url: str, timeout: float = 20) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def parse_stories(data: bytes, feed: Feed) -> list[Story]:
    parsed = feedparser.parse(data)
    if not parsed.entries:
        if parsed.get("bozo"):
            raise FeedError(f"unreadable feed ({type(parsed.get('bozo_exception')).__name__})")
        raise FeedError("feed contains no entries")
    stories = []
    for entry in parsed.entries:
        title = " ".join((entry.get("title") or "").split())
        link = (entry.get("link") or "").strip()
        stamp = entry.get("published_parsed") or entry.get("updated_parsed")
        if not (title and link and stamp):
            continue  # undated or incomplete entries cannot be placed in the time window
        published = datetime(*stamp[:6], tzinfo=timezone.utc)
        stories.append(Story(title=title, link=link, source=feed.name, published=published))
    return stories


def fetch_all(feeds: list[Feed], fetcher: Fetcher = http_get) -> tuple[list[Story], list[tuple[Feed, str]]]:
    """Return (stories from all working feeds, [(failed feed, reason), ...])."""
    stories: list[Story] = []
    failures: list[tuple[Feed, str]] = []
    for feed in feeds:
        try:
            feed_stories = parse_stories(fetcher(feed.url), feed)
        except Exception as exc:  # network, HTTP, parse: all are per-feed failures
            reason = f"{type(exc).__name__}: {exc}"
            log.warning("Feed failed, continuing with the others: %s (%s) - %s", feed.name, feed.url, reason)
            failures.append((feed, reason))
            continue
        log.info("Feed OK: %s - %d dated entries", feed.name, len(feed_stories))
        stories.extend(feed_stories)
    return stories, failures
