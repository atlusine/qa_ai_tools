"""Long-polling bot logic. No public URL or open port is needed: the bot asks Telegram for new messages.

Anyone who opens the bot gets a persistent "Get AI news digest" button. Pressing it (or sending /digest)
sends the current digest to that chat. To protect the RSS sources and keep replies fast:
- one digest is built at most every CACHE_SECONDS and shared by everyone who asks in that period;
- each chat can ask at most once per COOLDOWN_SECONDS;
- presses older than MAX_UPDATE_AGE_SECONDS (queued while the bot was offline) are ignored.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from news_digest.build import DEFAULT_FEEDS_FILE, AllFeedsFailed, build_digest, load_settings
from news_digest.feeds import Fetcher, http_get
from notifier.config import TelegramConfig
from notifier.telegram import TelegramError, call_api, split_message

log = logging.getLogger("bot")

BUTTON_TEXT = "📰 Get AI news digest"
KEYBOARD = {"keyboard": [[{"text": BUTTON_TEXT}]], "resize_keyboard": True, "is_persistent": True}
COMMANDS = [
    {"command": "digest", "description": "Get the latest AI news digest"},
    {"command": "start", "description": "Show the digest button"},
]

WELCOME = ("👋 Hi! I collect the top AI news stories from the last day.\n\n"
           f"Tap “{BUTTON_TEXT}” below, or send /digest, whenever you want the latest digest.")
HINT = f"Tap “{BUTTON_TEXT}” below, or send /digest, to get the latest AI news."
NO_STORIES = "📭 No new AI stories in the last day. Please check again later."
FEEDS_DOWN = "⚠️ I couldn't reach the news sources right now. Please try again in a few minutes."
BUILD_FAILED = "⚠️ Something went wrong while building the digest. Please try again later."

CACHE_SECONDS = 600
COOLDOWN_SECONDS = 30
MAX_UPDATE_AGE_SECONDS = 600
POLL_TIMEOUT_SECONDS = 50

Api = Callable[[str, "dict | None", float], dict]
DigestBuilder = Callable[[], "str | None"]  # may raise AllFeedsFailed


def make_builder(feeds_file: str | Path = DEFAULT_FEEDS_FILE, fetcher: Fetcher = http_get,
                 now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> DigestBuilder:
    """Settings are re-read on every build, so edits to feeds.txt apply without a restart."""
    def build() -> str | None:
        return build_digest(load_settings(feeds_file), now(), fetcher)
    return build


class DigestBot:
    def __init__(self, token: str, build: DigestBuilder, *, api: Api | None = None,
                 clock: Callable[[], float] = time.monotonic, wall_clock: Callable[[], float] = time.time,
                 cache_seconds: float = CACHE_SECONDS, cooldown_seconds: float = COOLDOWN_SECONDS,
                 max_update_age: float = MAX_UPDATE_AGE_SECONDS) -> None:
        config = TelegramConfig(token=token, chat_id="")  # chat is chosen per call
        self._api: Api = api or (lambda method, payload=None, timeout=15: call_api(config, method, payload, timeout))
        self._build = build
        self._clock = clock
        self._wall_clock = wall_clock
        self.cache_seconds = cache_seconds
        self.cooldown_seconds = cooldown_seconds
        self.max_update_age = max_update_age
        self._cache: tuple[float, str | None] | None = None
        self._last_request: dict[int, float] = {}

    # --- Telegram helpers -------------------------------------------------------------

    def setup(self) -> str:
        """Check the token, make sure long polling works, register the command menu. Returns the bot username."""
        me = self._api("getMe", None, 15)["result"]
        self._api("deleteWebhook", None, 15)  # getUpdates is refused while a webhook is set
        self._api("setMyCommands", {"commands": COMMANDS}, 15)
        return me.get("username", "?")

    def _send(self, chat_id: int, text: str, keyboard: bool = False) -> None:
        for chunk in split_message(text):
            payload = {"chat_id": chat_id, "text": chunk, "link_preview_options": {"is_disabled": True}}
            if keyboard:
                payload["reply_markup"] = KEYBOARD
            self._api("sendMessage", payload, 15)

    # --- message handling -------------------------------------------------------------

    def handle_update(self, update: dict) -> None:
        message = update.get("message")
        if not message:
            return
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            return
        age = self._wall_clock() - message.get("date", 0)
        if age > self.max_update_age:
            log.info("Ignoring a %.0f-minute-old message from chat %s (sent while the bot was offline)", age / 60, chat_id)
            return

        text = (message.get("text") or "").strip()
        command = text.split()[0].split("@")[0].lower() if text.startswith("/") else ""
        if command in ("/start", "/help"):
            self._send(chat_id, WELCOME, keyboard=True)
        elif text == BUTTON_TEXT or command == "/digest":
            self._send_digest(chat_id)
        elif chat.get("type") == "private":
            self._send(chat_id, HINT, keyboard=True)
        # Other group chatter is ignored.

    def _send_digest(self, chat_id: int) -> None:
        now = self._clock()
        last = self._last_request.get(chat_id)
        if last is not None and now - last < self.cooldown_seconds:
            wait = int(self.cooldown_seconds - (now - last)) + 1
            self._send(chat_id, f"⏳ Please wait {wait}s before asking again.")
            return
        self._last_request[chat_id] = now
        self._forget_old_requests(now)

        try:
            text = self._digest_text(chat_id, now)
        except AllFeedsFailed as exc:
            log.error("%s", exc)
            self._send(chat_id, FEEDS_DOWN)
            return
        except Exception:
            log.exception("Building the digest failed")
            self._send(chat_id, BUILD_FAILED)
            return

        if text is None:
            self._send(chat_id, NO_STORIES)
        else:
            self._send(chat_id, text)
            log.info("Digest sent to chat %s", chat_id)

    def _digest_text(self, chat_id: int, now: float) -> str | None:
        if self._cache is not None and now - self._cache[0] < self.cache_seconds:
            return self._cache[1]
        try:
            self._api("sendChatAction", {"chat_id": chat_id, "action": "typing"}, 15)
        except TelegramError:
            pass  # cosmetic only
        text = self._build()  # failures are not cached, so the next request retries
        self._cache = (now, text)
        return text

    def _forget_old_requests(self, now: float) -> None:
        if len(self._last_request) > 1000:
            self._last_request = {c: t for c, t in self._last_request.items() if now - t < self.cooldown_seconds}

    # --- polling loop -----------------------------------------------------------------

    def poll_once(self, offset: int | None) -> int | None:
        payload: dict = {"timeout": POLL_TIMEOUT_SECONDS, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        updates = self._api("getUpdates", payload, POLL_TIMEOUT_SECONDS + 15)["result"]
        for update in updates:
            offset = update["update_id"] + 1  # advance first: a failing update is never retried forever
            try:
                self.handle_update(update)
            except TelegramError as exc:
                log.warning("Could not reply (the user may have blocked the bot): %s", exc)
            except Exception:
                log.exception("Unexpected error while handling update %s", update.get("update_id"))
        return offset

    def run_forever(self, sleep: Callable[[float], None] = time.sleep) -> None:
        offset: int | None = None
        backoff = 0
        while True:
            try:
                offset = self.poll_once(offset)
                backoff = 0
            except TelegramError as exc:
                backoff = min(60, backoff * 2 or 5)
                if "409" in str(exc):
                    log.warning("Another copy of this bot is already running (Telegram returned 409). "
                                "Stop the other copy. Retrying in %ds.", backoff)
                else:
                    log.warning("%s; retrying in %ds", exc, backoff)
                sleep(backoff)
