"""Phase 1: digest selection, duplicate removal, formatting and end-to-end CLI behaviour."""
from datetime import datetime, timezone
from urllib.error import URLError

import pytest

from news_digest.__main__ import run
from news_digest.digest import dedupe, format_digest, normalize_link, normalize_title, select_recent
from news_digest.feeds import Feed, fetch_all, parse_feed_list

NOW = datetime(2026, 11, 25, 8, 0, tzinfo=timezone.utc)

FEEDS_TEXT = """
# comment
AI Wire | https://feeds.test/a.xml
ML Daily | https://feeds.test/b.xml
"""


def make_fetcher(fixtures_dir, mapping):
    """mapping: url -> fixture filename, or an Exception instance to raise."""
    def fetch(url):
        target = mapping[url]
        if isinstance(target, Exception):
            raise target
        return (fixtures_dir / target).read_bytes()
    return fetch


@pytest.fixture
def two_feeds(fixtures_dir):
    feeds = parse_feed_list(FEEDS_TEXT)
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/a.xml": "rss_a.xml", "https://feeds.test/b.xml": "atom_b.xml"})
    return feeds, fetcher


def write_feeds(tmp_path, text):
    path = tmp_path / "feeds.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


# --- unit level ---------------------------------------------------------------

def test_feed_list_parsing():
    feeds = parse_feed_list(FEEDS_TEXT + "https://plain.test/rss; Other | https://o.test/feed")
    assert [f.name for f in feeds] == ["AI Wire", "ML Daily", "plain.test", "Other"]


def test_comments_with_separators_are_ignored():
    feeds = parse_feed_list('# separated by newlines or ";" in RSS_FEEDS\nA | https://a.test/rss\n')
    assert feeds == [Feed("A", "https://a.test/rss")]


def test_repository_feeds_file_is_valid():
    from news_digest.__main__ import DEFAULT_FEEDS_FILE
    feeds = parse_feed_list(DEFAULT_FEEDS_FILE.read_text(encoding="utf-8"))
    assert len(feeds) >= 3
    assert all(f.url.startswith("https://") and f.name for f in feeds)


def test_normalization_rules():
    assert normalize_link("http://WWW.Example.com/news/model/?utm_source=rss&id=7#top") == "https://example.com/news/model?id=7"
    assert normalize_title("Regulators Publish AI Guidance - FAQ!") == normalize_title("Regulators publish AI guidance & FAQ")


def test_duplicates_removed_by_link_and_title(two_feeds):
    feeds, fetcher = two_feeds
    stories, failures = fetch_all(feeds, fetcher)
    assert not failures
    titles = [s.title for s in dedupe(stories)]
    assert "New open reasoning model from the lab" not in titles  # same link as AI Wire item
    assert "Regulators Publish AI Guidance - FAQ!" not in titles  # same title as AI Wire item
    assert "Lab releases a new open reasoning model" in titles
    assert len(titles) == len(set(titles))


def test_selects_up_to_five_recent_newest_first(two_feeds):
    feeds, fetcher = two_feeds
    stories, _ = fetch_all(feeds, fetcher)
    selected = select_recent(dedupe(stories), NOW, window_hours=24, limit=5)
    assert [s.title for s in selected] == [
        "Chip maker unveils AI accelerator",           # 07:30
        "Lab releases a new open reasoning model",     # 06:00
        "Regulators publish AI guidance & FAQ",        # 03:00
        "Robotics startup raises Series B",            # yesterday 20:00
        "Open-source LLM tops a coding benchmark",     # yesterday 12:00
    ]  # 6th recent story (09:30 yesterday) dropped by the limit; old/undated ones excluded


def test_window_is_configurable(two_feeds):
    feeds, fetcher = two_feeds
    stories, _ = fetch_all(feeds, fetcher)
    assert len(select_recent(dedupe(stories), NOW, window_hours=6, limit=5)) == 3


def test_format_contains_title_source_and_link(two_feeds):
    feeds, fetcher = two_feeds
    stories, _ = fetch_all(feeds, fetcher)
    selected = select_recent(dedupe(stories), NOW)
    text = format_digest(selected, NOW, 24, feeds_checked=3, feeds_failed=1)
    assert text.startswith("🤖 AI News Digest — 25 Nov 2026")
    assert "1. Chip maker unveils AI accelerator\n   Source: ML Daily · 25 Nov 07:30 UTC\n   https://mldaily.example.org/chip" in text
    assert "Source: AI Wire" in text
    assert text.rstrip().endswith("Top 5 stories from the last 24h · 3 feeds checked (1 unavailable)")


# --- end to end via the CLI entry point (network and Telegram mocked) ------------

def test_preview_prints_without_credentials(tmp_path, fixtures_dir, capsys, telegram_calls):
    path = write_feeds(tmp_path, FEEDS_TEXT)
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/a.xml": "rss_a.xml", "https://feeds.test/b.xml": "atom_b.xml"})
    assert run(["--preview", "--feeds-file", path], now=NOW, fetcher=fetcher) == 0
    out = capsys.readouterr().out
    assert "AI News Digest" in out and out.count("Source:") == 5
    assert telegram_calls == []


def test_send_uses_configured_chat(tmp_path, fixtures_dir, telegram_env, telegram_calls):
    path = write_feeds(tmp_path, FEEDS_TEXT)
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/a.xml": "rss_a.xml", "https://feeds.test/b.xml": "atom_b.xml"})
    assert run(["--feeds-file", path], now=NOW, fetcher=fetcher) == 0
    assert len(telegram_calls) == 1
    url, payload = telegram_calls[0]
    assert url.endswith("/sendMessage")
    assert payload["chat_id"] == "424242"
    assert "parse_mode" not in payload  # plain text
    assert "Chip maker unveils AI accelerator" in payload["text"]


def test_partial_feed_failure_continues(tmp_path, fixtures_dir, capsys, caplog):
    path = write_feeds(tmp_path, FEEDS_TEXT + "Broken | https://feeds.test/broken.xml\n")
    fetcher = make_fetcher(fixtures_dir, {
        "https://feeds.test/a.xml": "rss_a.xml",
        "https://feeds.test/b.xml": "atom_b.xml",
        "https://feeds.test/broken.xml": URLError("connection refused"),
    })
    assert run(["--preview", "--feeds-file", path], now=NOW, fetcher=fetcher) == 0
    assert "Feed failed, continuing" in caplog.text and "Broken" in caplog.text
    assert "3 feeds checked (1 unavailable)" in capsys.readouterr().out


def test_unparseable_feed_counts_as_failure(tmp_path, fixtures_dir):
    path = write_feeds(tmp_path, "Bad | https://feeds.test/bad\n")
    fixtures = tmp_path / "html"
    fixtures.mkdir()
    (fixtures / "page.html").write_text("<html><body>not a feed</body></html>")
    assert run(["--preview", "--feeds-file", path], now=NOW, fetcher=make_fetcher(fixtures, {"https://feeds.test/bad": "page.html"})) == 2


def test_all_feeds_fail_returns_clear_error(tmp_path, caplog, capsys, telegram_env, telegram_calls):
    path = write_feeds(tmp_path, FEEDS_TEXT)
    fetcher = make_fetcher(None, {"https://feeds.test/a.xml": URLError("timeout"), "https://feeds.test/b.xml": TimeoutError("timed out")})
    assert run(["--feeds-file", path], now=NOW, fetcher=fetcher) == 2
    assert "All 2 feeds failed; no digest was produced" in caplog.text
    assert telegram_calls == []
    assert capsys.readouterr().out == ""


def test_no_recent_stories_logs_and_skips_send(tmp_path, fixtures_dir, caplog, capsys, telegram_env, telegram_calls):
    caplog.set_level("INFO")
    path = write_feeds(tmp_path, "Quiet | https://feeds.test/quiet.xml\n")
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/quiet.xml": "old_only.xml"})
    assert run(["--feeds-file", path], now=NOW, fetcher=fetcher) == 0
    assert "No stories published in the last 24h" in caplog.text and "skipping send" in caplog.text
    assert telegram_calls == []


def test_rss_feeds_env_overrides_file(tmp_path, fixtures_dir, monkeypatch, capsys):
    path = write_feeds(tmp_path, "Ignored | https://feeds.test/ignored.xml\n")
    monkeypatch.setenv("RSS_FEEDS", "Quiet | https://feeds.test/quiet.xml; AI Wire | https://feeds.test/a.xml")
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/quiet.xml": "old_only.xml", "https://feeds.test/a.xml": "rss_a.xml"})
    assert run(["--preview", "--feeds-file", path, "--max-stories", "2"], now=NOW, fetcher=fetcher) == 0
    assert capsys.readouterr().out.count("Source: AI Wire") == 2


def test_send_without_credentials_is_config_error(tmp_path, fixtures_dir, caplog, telegram_calls):
    path = write_feeds(tmp_path, FEEDS_TEXT)
    fetcher = make_fetcher(fixtures_dir, {"https://feeds.test/a.xml": "rss_a.xml", "https://feeds.test/b.xml": "atom_b.xml"})
    assert run(["--feeds-file", path], now=NOW, fetcher=fetcher) == 3
    assert "Missing required environment variable(s): TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID" in caplog.text
    assert telegram_calls == []
