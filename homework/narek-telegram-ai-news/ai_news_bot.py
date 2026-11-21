#!/usr/bin/env python3
"""Daily AI news to Telegram.

Reads a few AI news RSS/Atom feeds, picks the 5 newest unique stories
and sends them to one Telegram chat.

Usage:
  python3 ai_news_bot.py --dry-run      # print the message, send nothing
  python3 ai_news_bot.py --get-chat-id  # show chat IDs that messaged the bot
  python3 ai_news_bot.py                # fetch and send to Telegram

Secrets come from .env next to this file (never commit it):
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHAT_ID=...

Standard library only, so no pip install is needed.
"""

import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed",
    "https://venturebeat.com/category/ai/feed/",
]
TOP_N = 5
TIMEOUT = 15
USER_AGENT = "ai-news-bot/1.0 (course exercise)"
ATOM = "{http://www.w3.org/2005/Atom}"
OLD = datetime(1970, 1, 1, tzinfo=timezone.utc)


def load_env(path):
    """Tiny .env reader: KEY=VALUE lines, # comments ignored."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read()


def parse_date(text):
    if not text:
        return OLD
    text = text.strip()
    try:  # RSS: "Thu, 20 Nov 2026 10:00:00 +0000"
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:  # Atom: "2026-11-20T10:00:00Z"
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return OLD
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_feed(xml_bytes, source):
    """Return a list of {title, link, date, source} from RSS or Atom."""
    root = ET.fromstring(xml_bytes)
    items = []
    for it in root.iter("item"):  # RSS 2.0
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "date": parse_date(it.findtext("pubDate")),
            "source": source,
        })
    for entry in root.iter(ATOM + "entry"):  # Atom
        link = ""
        for l in entry.findall(ATOM + "link"):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href", "")
                break
        items.append({
            "title": (entry.findtext(ATOM + "title") or "").strip(),
            "link": link.strip(),
            "date": parse_date(entry.findtext(ATOM + "published")
                               or entry.findtext(ATOM + "updated")),
            "source": source,
        })
    return [i for i in items if i["title"] and i["link"]]


def fetch_all(feeds):
    stories, errors = [], []
    for url in feeds:
        source = urllib.parse.urlparse(url).netloc.replace("www.", "")
        try:
            stories.extend(parse_feed(http_get(url), source))
        except Exception as exc:  # one bad feed must not kill the run
            errors.append("{}: {}".format(source, exc))
    return stories, errors


def top_stories(stories, n=TOP_N):
    """Newest first, no duplicate links or titles."""
    seen, result = set(), []
    for s in sorted(stories, key=lambda s: s["date"], reverse=True):
        key_link = s["link"].split("?")[0].rstrip("/")
        key_title = s["title"].lower()
        if key_link in seen or key_title in seen:
            continue
        seen.update([key_link, key_title])
        result.append(s)
        if len(result) == n:
            break
    return result


def build_message(stories):
    today = datetime.now().strftime("%d %b %Y")
    lines = ["<b>🤖 AI news, {}</b>".format(today), ""]
    for i, s in enumerate(stories, 1):
        lines.append('{}. <a href="{}">{}</a> <i>({})</i>'.format(
            i, html.escape(s["link"], quote=True), html.escape(s["title"]),
            html.escape(s["source"])))
    return "\n".join(lines)


def telegram(method, token, params=None):
    url = "https://api.telegram.org/bot{}/{}".format(token, method)
    data = urllib.parse.urlencode(params).encode() if params else None
    req = urllib.request.Request(url, data=data)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        # Don't print the URL: it contains the token.
        body = exc.read().decode(errors="replace")
        raise SystemExit("Telegram {} failed: HTTP {} {}".format(method, exc.code, body))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print, don't send")
    parser.add_argument("--get-chat-id", action="store_true",
                        help="list chats that messaged the bot")
    args = parser.parse_args()

    load_env(Path(__file__).with_name(".env"))
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")

    if args.get_chat_id:
        if not token:
            sys.exit("TELEGRAM_BOT_TOKEN missing in .env")
        updates = telegram("getUpdates", token).get("result", [])
        chats = {u["message"]["chat"]["id"]: u["message"]["chat"].get("first_name", "")
                 for u in updates if "message" in u}
        if not chats:
            sys.exit("No messages yet. Send your bot any message in Telegram, then retry.")
        for cid, name in chats.items():
            print("chat id {} ({})".format(cid, name))
        return

    stories, errors = fetch_all(FEEDS)
    for e in errors:
        print("WARN feed failed: " + e, file=sys.stderr)
    top = top_stories(stories)
    if not top:
        sys.exit("No stories from any feed, nothing sent.")
    message = build_message(top)

    if args.dry_run:
        print(message)
        return

    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        sys.exit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")
    result = telegram("sendMessage", token, {
        "chat_id": chat_id, "text": message, "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    })
    if not result.get("ok"):
        sys.exit("Telegram said not ok: {}".format(result))
    print("Sent {} stories to chat {}".format(len(top), chat_id))


if __name__ == "__main__":
    main()
