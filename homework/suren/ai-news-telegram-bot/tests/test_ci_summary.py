"""Phase 2: CI summary classification and messages (Telegram mocked)."""
import shutil
from urllib.error import URLError

import pytest

import notifier.ci_summary as ci
import notifier.telegram as tg
from notifier.ci_summary import PASSED, PIPELINE_FAILED, TESTS_FAILED, build_message, classify, parse_junit
from tests.conftest import FAKE_TOKEN

BASE_ENV = {
    "GITHUB_REPOSITORY": "student/ai-news-telegram-bot",
    "GITHUB_SERVER_URL": "https://github.com",
    "GITHUB_RUN_ID": "987654321",
    "GITHUB_RUN_ATTEMPT": "1",
    "GITHUB_WORKFLOW": "CI tests with Telegram summary (demo)",
    "GITHUB_REF_NAME": "main",
    "CI_SUITE": "Unit tests (pytest)",
    "CI_JOB": "Unit tests",
}


@pytest.fixture
def report(tmp_path, fixtures_dir):
    def make(name):
        target = tmp_path / "reports" / "junit.xml"
        target.parent.mkdir(exist_ok=True)
        shutil.copy(fixtures_dir / name, target)
        return str(target)
    return make


def env(**overrides):
    return {**BASE_ENV, **overrides}


def test_parse_junit_counts(fixtures_dir):
    counts = parse_junit(fixtures_dir / "junit_fail.xml")
    assert (counts.passed, counts.failed, counts.errors, counts.skipped, counts.total) == (3, 1, 1, 1, 6)
    assert counts.failed_names == ["tests.demo.test_demo_scenario::test_demo_scenario_gate",
                                   "tests.test_checkout::test_payment_fixture"]


def test_parse_junit_missing_returns_none(tmp_path):
    assert parse_junit(tmp_path / "nope.xml") is None


def test_success_message(report):
    msg = build_message(env(CI_JOB_RESULT="success", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="success",
                            CI_REPORT_PATH=report("junit_pass.xml")))
    assert msg.splitlines()[0] == "✅ Tests passed"
    for expected in ("Repository: student/ai-news-telegram-bot", "Suite / job: Unit tests (pytest) / Unit tests",
                     "Branch: main", "Tests: 3 passed, 0 failed, 1 skipped (4 total)",
                     "Run: https://github.com/student/ai-news-telegram-bot/actions/runs/987654321"):
        assert expected in msg
    assert "DEMO" not in msg


def test_test_failure_message_lists_failed_tests(report):
    msg = build_message(env(CI_JOB_RESULT="failure", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="failure",
                            CI_REPORT_PATH=report("junit_fail.xml")))
    assert msg.splitlines()[0] == "❌ Tests failed"
    assert "Tests: 3 passed, 2 failed, 1 skipped (6 total); 1 of the failures are errors" in msg
    assert " • tests.demo.test_demo_scenario::test_demo_scenario_gate" in msg


def test_pipeline_failure_says_tests_did_not_run(tmp_path):
    msg = build_message(env(CI_JOB_RESULT="failure", CI_SETUP_OUTCOME="failure", CI_TESTS_OUTCOME="skipped",
                            CI_REPORT_PATH=str(tmp_path / "missing.xml")))
    assert msg.splitlines()[0] == "🛠 Pipeline failure: tests did not run"
    assert "Result: Tests did not run: the setup / build step failed." in msg
    assert "Tests: Tests did not run, so there is no test report." in msg
    assert "passed" not in msg


def test_job_never_started_is_pipeline_failure():
    s = classify(job_result="skipped", setup_outcome="", tests_outcome="", counts=None)
    assert s.status == PIPELINE_FAILED and "did not start" in s.detail


def test_failed_tests_without_report_is_explicit(tmp_path):
    msg = build_message(env(CI_JOB_RESULT="failure", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="failure",
                            CI_REPORT_PATH=str(tmp_path / "missing.xml")))
    assert msg.splitlines()[0] == "❌ Tests failed"
    assert "Tests: No test report found; counts unavailable." in msg


def test_success_without_report_is_explicit(tmp_path):
    msg = build_message(env(CI_JOB_RESULT="success", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="success",
                            CI_REPORT_PATH=str(tmp_path / "missing.xml")))
    assert msg.splitlines()[0] == "✅ Tests passed"
    assert "No test report found; counts unavailable." in msg


def test_malformed_report_is_reported(tmp_path):
    bad = tmp_path / "junit.xml"
    bad.write_text("<testsuites><testsuite", encoding="utf-8")
    msg = build_message(env(CI_JOB_RESULT="failure", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="failure",
                            CI_REPORT_PATH=str(bad)))
    assert "Test report could not be read: malformed JUnit XML" in msg


def test_report_failures_win_over_step_outcome(fixtures_dir):
    counts = parse_junit(fixtures_dir / "junit_fail.xml")
    assert classify("failure", "success", "failure", counts).status == TESTS_FAILED


def test_tests_passed_but_later_step_failed(fixtures_dir):
    counts = parse_junit(fixtures_dir / "junit_pass.xml")
    s = classify("failure", "success", "success", counts)
    assert s.status == PIPELINE_FAILED and "later pipeline step" in s.detail


def test_cancelled_before_tests():
    assert classify("cancelled", "success", "cancelled", None).status == "cancelled"


def test_demo_label(report):
    msg = build_message(env(CI_DEMO="true", CI_SCENARIO="success", CI_JOB_RESULT="success",
                            CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="success", CI_REPORT_PATH=report("junit_pass.xml")))
    first, second = msg.splitlines()[:2]
    assert first.startswith("[DEMO] Simulated scenario: success")
    assert second == "[DEMO] ✅ Tests passed"


def test_run_attempt_in_link():
    msg = build_message(env(GITHUB_RUN_ATTEMPT="2", CI_JOB_RESULT="success", CI_TESTS_OUTCOME="success"))
    assert "actions/runs/987654321/attempts/2" in msg


# --- CLI: delivery and error isolation ---------------------------------------------

def test_cli_sends_summary(monkeypatch, telegram_env, telegram_calls, report):
    for key, value in env(CI_JOB_RESULT="success", CI_SETUP_OUTCOME="success", CI_TESTS_OUTCOME="success",
                          CI_REPORT_PATH=report("junit_pass.xml")).items():
        monkeypatch.setenv(key, value)
    assert ci.main([]) == 0
    assert telegram_calls[0][1]["text"].startswith("✅ Tests passed")


def test_cli_telegram_error_is_logged_separately(monkeypatch, telegram_env, caplog, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("CI_JOB_RESULT", "failure")
    monkeypatch.setenv("CI_SETUP_OUTCOME", "failure")

    def boom(request, timeout=None):
        raise URLError(f"connection reset for bot{FAKE_TOKEN}")

    monkeypatch.setattr(tg, "urlopen", boom)
    assert ci.main([]) == 1  # delivery error exit code; the workflow uses continue-on-error
    out = capsys.readouterr().out
    assert "::warning title=Telegram delivery failed::" in out
    assert FAKE_TOKEN not in out + caplog.text
