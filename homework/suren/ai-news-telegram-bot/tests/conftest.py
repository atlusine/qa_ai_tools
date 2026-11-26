import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

FAKE_TOKEN = "123456789:FAKE-test-token-never-real"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """Run every test in an empty directory without real Telegram/GitHub variables,
    so a developer's local .env can never be read or used by the tests."""
    for name in list(os.environ):
        if name.startswith(("TELEGRAM_", "DIGEST_", "CI_", "GITHUB_")) or name == "RSS_FEEDS":
            monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def telegram_calls(monkeypatch):
    """Replace the network call to Telegram; records (url, json_payload) tuples."""
    import json
    import notifier.telegram as tg

    calls = []

    def fake_urlopen(request, timeout=None):
        calls.append((request.full_url, json.loads(request.data.decode("utf-8"))))
        return FakeResponse(b'{"ok": true, "result": {}}')

    monkeypatch.setattr(tg, "urlopen", fake_urlopen)
    return calls


@pytest.fixture
def telegram_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", FAKE_TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "424242")
