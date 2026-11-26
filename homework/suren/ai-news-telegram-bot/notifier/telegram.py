"""Send plain-text messages to Telegram via the Bot API.

Library use:
    from notifier.telegram import send_message
    send_message("Hello")              # uses TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID

Command line:
    python -m notifier.telegram --text "Hello"
    python -m notifier.telegram --file message.txt
    some_command | python -m notifier.telegram
    python -m notifier.telegram --preview --text "Hello"   # print only, no credentials needed

Exit codes: 0 sent/previewed, 1 Telegram delivery error, 3 configuration/usage error.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from notifier.config import ConfigError, TelegramConfig, ensure_utf8_output, get_telegram_config, load_dotenv

log = logging.getLogger("notifier.telegram")

API_BASE = "https://api.telegram.org"
MAX_MESSAGE_LENGTH = 4096  # Telegram limit for a single text message

EXIT_OK, EXIT_DELIVERY_ERROR, EXIT_CONFIG_ERROR = 0, 1, 3


class TelegramError(Exception):
    """Delivery failed. The message is already redacted (never contains the token)."""


def redact(text: str, token: str | None) -> str:
    return text.replace(token, "***") if token else text


def split_message(text: str, limit: int = MAX_MESSAGE_LENGTH) -> list[str]:
    """Split on line boundaries so each chunk fits Telegram's length limit."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:  # a single very long line: hard split
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        if len(current) + len(line) > limit:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return [c.rstrip("\n") for c in chunks if c.strip()]


def call_api(config: TelegramConfig, method: str, payload: dict | None = None, timeout: float = 15) -> dict:
    """Call a Bot API method. Errors are raised as TelegramError with the token removed."""
    url = f"{API_BASE}/bot{config.token}/{method}"
    data = json.dumps(payload or {}).encode("utf-8")
    request = Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = ""
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("description", "")
        except Exception:  # body missing or not JSON
            pass
        msg = f"Telegram API {method} returned HTTP {exc.code}" + (f": {detail}" if detail else "")
        raise TelegramError(redact(msg, config.token)) from None
    except (URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        raise TelegramError(redact(f"Could not reach Telegram ({type(exc).__name__}: {reason})", config.token)) from None
    if not body.get("ok"):
        raise TelegramError(redact(f"Telegram API {method} failed: {body.get('description', 'unknown error')}", config.token))
    return body


def send_message(text: str, config: TelegramConfig | None = None, timeout: float = 15) -> int:
    """Send `text` as plain text (no Markdown/HTML parsing). Returns the number of messages sent."""
    if not text or not text.strip():
        raise ValueError("Refusing to send an empty message")
    config = config or get_telegram_config()
    chunks = split_message(text)
    for chunk in chunks:
        call_api(
            config,
            "sendMessage",
            {
                "chat_id": config.chat_id,
                "text": chunk,
                "link_preview_options": {"is_disabled": True},
            },
            timeout=timeout,
        )
    return len(chunks)


def report_delivery_error(message: str) -> None:
    """Log a delivery error; add a GitHub Actions annotation when running in Actions."""
    log.error("Telegram delivery failed: %s", message)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning title=Telegram delivery failed::{message}", flush=True)


def deliver(text: str, preview: bool) -> int:
    """Shared CLI behaviour: print in preview mode, otherwise send. Returns an exit code."""
    if preview:
        print(text)
        return EXIT_OK
    try:
        config = get_telegram_config()
    except ConfigError as exc:
        log.error("%s", exc)
        return EXIT_CONFIG_ERROR
    try:
        count = send_message(text, config)
    except TelegramError as exc:
        report_delivery_error(str(exc))
        return EXIT_DELIVERY_ERROR
    log.info("Telegram message delivered (%d part%s)", count, "" if count == 1 else "s")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="python -m notifier.telegram", description="Send a plain-text Telegram message.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="message text")
    source.add_argument("--file", help="read the message from a UTF-8 file")
    parser.add_argument("--preview", action="store_true", help="print the message instead of sending it")
    args = parser.parse_args(argv)

    load_dotenv()
    if args.text is not None:
        text = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as fh:
            text = fh.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.error("provide --text, --file, or pipe the message on stdin")
    if not text.strip():
        log.error("Message is empty; nothing to send")
        return EXIT_CONFIG_ERROR
    return deliver(text, args.preview)


if __name__ == "__main__":
    sys.exit(main())
