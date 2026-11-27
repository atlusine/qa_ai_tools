"""Shared Telegram notifier: delivery, CLI, splitting, .env loading and token redaction."""
import io
import json
from urllib.error import HTTPError, URLError

import pytest

import notifier.telegram as tg
from notifier.config import ConfigError, TelegramConfig, get_telegram_config, load_dotenv
from tests.conftest import FAKE_TOKEN

CONFIG = TelegramConfig(token=FAKE_TOKEN, chat_id="424242")


def test_send_message_posts_plain_text(telegram_calls):
    assert tg.send_message("Hello <b>world</b> $(whoami)", CONFIG) == 1
    url, payload = telegram_calls[0]
    assert url == f"https://api.telegram.org/bot{FAKE_TOKEN}/sendMessage"
    assert payload == {"chat_id": "424242", "text": "Hello <b>world</b> $(whoami)", "link_preview_options": {"is_disabled": True}}


def test_long_messages_are_split(telegram_calls):
    text = "\n".join(f"line {i} " + "x" * 80 for i in range(120))  # ~10k chars
    assert tg.send_message(text, CONFIG) == len(telegram_calls) >= 3
    assert all(len(p["text"]) <= tg.MAX_MESSAGE_LENGTH for _, p in telegram_calls)
    assert "".join(p["text"] for _, p in telegram_calls).replace("\n", "") == text.replace("\n", "")


def test_empty_message_rejected():
    with pytest.raises(ValueError):
        tg.send_message("   ", CONFIG)


def test_config_reports_missing_and_placeholder_values():
    with pytest.raises(ConfigError) as err:
        get_telegram_config({"TELEGRAM_BOT_TOKEN": "<your-bot-token>", "TELEGRAM_CHAT_ID": "1"})
    assert "TELEGRAM_BOT_TOKEN" in str(err.value) and "TELEGRAM_CHAT_ID" not in str(err.value)


def test_token_not_in_repr():
    assert FAKE_TOKEN not in repr(CONFIG)


def test_dotenv_loaded_but_real_env_wins(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text('TELEGRAM_BOT_TOKEN="from-file"\nTELEGRAM_CHAT_ID=from-file\n# comment\n')
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "from-env")
    load_dotenv(tmp_path / ".env")
    cfg = get_telegram_config()
    assert (cfg.token, cfg.chat_id) == ("from-file", "from-env")


def _raise(exc):
    def fake_urlopen(request, timeout=None):
        raise exc
    return fake_urlopen


@pytest.mark.parametrize("exc", [
    HTTPError(f"https://api.telegram.org/bot{FAKE_TOKEN}/sendMessage", 401, "Unauthorized", {},
              io.BytesIO(json.dumps({"ok": False, "description": "Unauthorized"}).encode())),
    URLError(f"failed to reach https://api.telegram.org/bot{FAKE_TOKEN}/sendMessage"),
    TimeoutError("timed out"),
])
def test_delivery_errors_never_contain_token(monkeypatch, exc):
    monkeypatch.setattr(tg, "urlopen", _raise(exc))
    with pytest.raises(tg.TelegramError) as err:
        tg.send_message("hi", CONFIG)
    assert FAKE_TOKEN not in str(err.value)
    assert err.value.__cause__ is None and err.value.__suppress_context__  # no chained traceback with the URL


def test_api_ok_false_is_error(monkeypatch):
    from tests.conftest import FakeResponse
    monkeypatch.setattr(tg, "urlopen", lambda r, timeout=None: FakeResponse(b'{"ok": false, "description": "chat not found"}'))
    with pytest.raises(tg.TelegramError, match="chat not found"):
        tg.send_message("hi", CONFIG)


# --- CLI ---------------------------------------------------------------------------

def test_cli_preview_needs_no_credentials(capsys, telegram_calls):
    assert tg.main(["--preview", "--text", "Preview me"]) == 0
    assert capsys.readouterr().out.strip() == "Preview me"
    assert telegram_calls == []


def test_cli_sends_text(telegram_env, telegram_calls):
    assert tg.main(["--text", "Build finished"]) == 0
    assert telegram_calls[0][1]["text"] == "Build finished"


def test_cli_reads_file(tmp_path, telegram_env, telegram_calls):
    (tmp_path / "msg.txt").write_text("From file ✅", encoding="utf-8")
    assert tg.main(["--file", str(tmp_path / "msg.txt")]) == 0
    assert telegram_calls[0][1]["text"] == "From file ✅"


def test_cli_missing_config_exit_3(caplog, telegram_calls):
    assert tg.main(["--text", "x"]) == 3
    assert "Missing required environment variable(s)" in caplog.text


def test_cli_delivery_error_exit_1_and_redacted(monkeypatch, telegram_env, caplog, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setattr(tg, "urlopen", _raise(URLError(f"bad host for bot{FAKE_TOKEN}")))
    assert tg.main(["--text", "x"]) == 1
    out = capsys.readouterr().out
    assert "::warning title=Telegram delivery failed::" in out
    assert FAKE_TOKEN not in out and FAKE_TOKEN not in caplog.text
