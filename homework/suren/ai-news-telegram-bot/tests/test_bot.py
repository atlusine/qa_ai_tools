"""Interactive bot: button/commands, caching, cooldown, error replies, polling loop."""
from datetime import datetime, timezone

import pytest

import bot.__main__ as bot_main
from bot.app import (BUILD_FAILED, BUTTON_TEXT, FEEDS_DOWN, HINT, KEYBOARD, NO_STORIES, WELCOME, DigestBot,
                     make_builder)
from news_digest.build import AllFeedsFailed
from notifier.config import ConfigError, get_bot_token
from notifier.telegram import MAX_MESSAGE_LENGTH, TelegramError
from tests.conftest import FAKE_TOKEN

NOW_WALL = 1_800_000_000.0


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class FakeApi:
    def __init__(self):
        self.calls = []
        self.updates = []
        self.fail_methods = {}

    def __call__(self, method, payload=None, timeout=15):
        self.calls.append((method, payload))
        if method in self.fail_methods:
            raise TelegramError(self.fail_methods[method])
        if method == "getUpdates":
            batch, self.updates = self.updates, []
            return {"ok": True, "result": batch}
        if method == "getMe":
            return {"ok": True, "result": {"username": "test_bot"}}
        return {"ok": True, "result": {}}

    def sent(self, chat_id=None):
        return [p for m, p in self.calls if m == "sendMessage" and (chat_id is None or p["chat_id"] == chat_id)]


class Builder:
    def __init__(self, result="🤖 AI News Digest — test"):
        self.result = result
        self.count = 0

    def __call__(self):
        self.count += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def msg(text, chat_id=7, chat_type="private", date=NOW_WALL, update_id=1):
    return {"update_id": update_id, "message": {"date": date, "text": text, "chat": {"id": chat_id, "type": chat_type}}}


@pytest.fixture
def env():
    api, clock, build = FakeApi(), FakeClock(), Builder()
    bot = DigestBot(FAKE_TOKEN, build, api=api, clock=clock, wall_clock=lambda: NOW_WALL)
    return bot, api, clock, build


def test_start_shows_persistent_button(env):
    bot, api, _, _ = env
    bot.handle_update(msg("/start"))
    [reply] = api.sent()
    assert reply["text"] == WELCOME and reply["reply_markup"] == KEYBOARD
    assert KEYBOARD["keyboard"][0][0]["text"] == BUTTON_TEXT and KEYBOARD["is_persistent"]


@pytest.mark.parametrize("text", [BUTTON_TEXT, "/digest", "/digest@test_bot"])
def test_button_and_command_send_digest_to_that_chat(env, text):
    bot, api, _, build = env
    bot.handle_update(msg(text, chat_id=555))
    assert ("sendChatAction", {"chat_id": 555, "action": "typing"}) in api.calls
    assert [p["text"] for p in api.sent(555)] == ["🤖 AI News Digest — test"]
    assert build.count == 1


def test_digest_is_cached_and_shared_between_chats(env):
    bot, api, clock, build = env
    bot.handle_update(msg(BUTTON_TEXT, chat_id=1))
    clock.t += 60
    bot.handle_update(msg(BUTTON_TEXT, chat_id=2))
    assert build.count == 1 and len(api.sent(2)) == 1
    clock.t += bot.cache_seconds
    bot.handle_update(msg(BUTTON_TEXT, chat_id=2))
    assert build.count == 2


def test_cooldown_per_chat(env):
    bot, api, clock, build = env
    bot.handle_update(msg(BUTTON_TEXT, chat_id=1))
    clock.t += 10
    bot.handle_update(msg(BUTTON_TEXT, chat_id=1))
    assert api.sent(1)[-1]["text"].startswith("⏳ Please wait 21s")
    bot.handle_update(msg(BUTTON_TEXT, chat_id=2))  # other chats are not affected
    assert api.sent(2)[-1]["text"] == "🤖 AI News Digest — test"
    clock.t += bot.cooldown_seconds
    bot.handle_update(msg(BUTTON_TEXT, chat_id=1))
    assert api.sent(1)[-1]["text"] == "🤖 AI News Digest — test"


@pytest.mark.parametrize("result, expected", [
    (None, NO_STORIES),
    (AllFeedsFailed("all down"), FEEDS_DOWN),
    (RuntimeError("bug"), BUILD_FAILED),
])
def test_friendly_replies_when_no_digest(result, expected):
    api, clock, build = FakeApi(), FakeClock(), Builder(result)
    bot = DigestBot(FAKE_TOKEN, build, api=api, clock=clock, wall_clock=lambda: NOW_WALL)
    bot.handle_update(msg(BUTTON_TEXT))
    assert api.sent()[-1]["text"] == expected


def test_failures_are_not_cached():
    api, clock, build = FakeApi(), FakeClock(), Builder(AllFeedsFailed("down"))
    bot = DigestBot(FAKE_TOKEN, build, api=api, clock=clock, wall_clock=lambda: NOW_WALL)
    bot.handle_update(msg(BUTTON_TEXT))
    clock.t += bot.cooldown_seconds
    build.result = "fresh"
    bot.handle_update(msg(BUTTON_TEXT))
    assert build.count == 2 and api.sent()[-1]["text"] == "fresh"


def test_long_digest_is_split(env):
    bot, api, _, build = env
    build.result = "\n".join("x" * 100 for _ in range(100))
    bot.handle_update(msg(BUTTON_TEXT))
    assert len(api.sent()) >= 3 and all(len(p["text"]) <= MAX_MESSAGE_LENGTH for p in api.sent())


def test_old_queued_messages_are_ignored(env):
    bot, api, _, build = env
    bot.handle_update(msg(BUTTON_TEXT, date=NOW_WALL - bot.max_update_age - 1))
    assert api.calls == [] and build.count == 0


def test_other_text_gets_hint_in_private_but_ignored_in_groups(env):
    bot, api, _, _ = env
    bot.handle_update(msg("hello", chat_id=1))
    bot.handle_update(msg("hello", chat_id=-100, chat_type="supergroup"))
    assert [p["text"] for p in api.sent()] == [HINT]
    bot.handle_update({"update_id": 9, "edited_message": {}})  # non-message updates are ignored
    assert len(api.calls) == 1


def test_poll_advances_offset_and_survives_errors(env):
    bot, api, _, _ = env
    api.updates = [msg("/start", update_id=10), msg(BUTTON_TEXT, update_id=11)]
    api.fail_methods["sendMessage"] = "Telegram API sendMessage returned HTTP 403: bot was blocked by the user"
    assert bot.poll_once(None) == 12
    assert bot.poll_once(12) == 12  # no new updates
    assert api.calls[-1] == ("getUpdates", {"timeout": 50, "allowed_updates": ["message"], "offset": 12})


def test_setup_registers_commands_and_removes_webhook(env):
    bot, api, _, _ = env
    assert bot.setup() == "test_bot"
    assert [m for m, _ in api.calls] == ["getMe", "deleteWebhook", "setMyCommands"]


def test_builder_uses_real_digest_pipeline(tmp_path, fixtures_dir):
    feeds = tmp_path / "feeds.txt"
    feeds.write_text("AI Wire | https://feeds.test/a.xml\n", encoding="utf-8")
    fetcher = lambda url: (fixtures_dir / "rss_a.xml").read_bytes()
    build = make_builder(feeds, fetcher, now=lambda: datetime(2026, 11, 25, 8, 0, tzinfo=timezone.utc))
    text = build()
    assert text.startswith("🤖 AI News Digest — 25 Nov 2026") and "Source: AI Wire" in text
    failing = make_builder(feeds, lambda url: (_ for _ in ()).throw(OSError("down")))
    with pytest.raises(AllFeedsFailed):
        failing()


def test_bot_token_config():
    assert get_bot_token({"TELEGRAM_BOT_TOKEN": FAKE_TOKEN}) == FAKE_TOKEN
    with pytest.raises(ConfigError):
        get_bot_token({"TELEGRAM_BOT_TOKEN": "<your-bot-token>"})


def test_main_without_token_exits_3(caplog):
    assert bot_main.main([]) == 3
    assert "TELEGRAM_BOT_TOKEN" in caplog.text and FAKE_TOKEN not in caplog.text
