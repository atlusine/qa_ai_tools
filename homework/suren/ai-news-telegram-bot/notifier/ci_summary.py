"""Send a CI test/pipeline summary to Telegram.

Designed for a separate GitHub Actions `notify` job that runs with `if: always()` after the
test job. All input comes from environment variables, so workflow data never goes through shell
interpolation:

  CI_JOB_RESULT      needs.<job>.result: success | failure | cancelled | skipped
  CI_SETUP_OUTCOME   outcome of the setup/build/install step: success | failure | skipped | cancelled
  CI_TESTS_OUTCOME   outcome of the step that runs the tests (same values)
  CI_REPORT_PATH     JUnit XML report path (optional; default reports/junit.xml)
  CI_SUITE           human name of the test suite (optional)
  CI_JOB             name of the job that ran the tests (optional)
  CI_DEMO            "true" to label the message as a demo (optional)
  CI_SCENARIO        demo scenario name shown in demo messages (optional)
  GITHUB_*           standard variables provided by GitHub Actions (repo, branch, run id ...)

    python -m notifier.ci_summary [--preview]

The exit code describes only Telegram delivery (0 ok, 1 delivery error, 3 config error), never the
test result. The workflow's own status stays the source of truth for pass/fail.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from notifier.config import ensure_utf8_output, load_dotenv
from notifier.telegram import deliver

log = logging.getLogger("notifier.ci_summary")

PASSED, TESTS_FAILED, PIPELINE_FAILED, CANCELLED = "passed", "tests_failed", "pipeline_failed", "cancelled"
HEADLINES = {
    PASSED: "✅ Tests passed",
    TESTS_FAILED: "❌ Tests failed",
    PIPELINE_FAILED: "🛠 Pipeline failure: tests did not run",
    CANCELLED: "⏹ Run cancelled",
}
MAX_FAILED_NAMES = 5


class ReportError(Exception):
    pass


@dataclass
class TestCounts:
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    failed_names: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.errors + self.skipped


def parse_junit(path: str | os.PathLike) -> TestCounts | None:
    """Count test cases in a JUnit XML report. Returns None if the file does not exist."""
    p = Path(path)
    if not p.is_file():
        return None
    try:
        root = ET.parse(p).getroot()
    except ET.ParseError as exc:
        raise ReportError(f"malformed JUnit XML ({exc})") from None
    if root.tag not in ("testsuites", "testsuite"):
        raise ReportError(f"unexpected root element <{root.tag}>")
    counts = TestCounts()
    for case in root.iter("testcase"):
        name = "::".join(filter(None, [case.get("classname"), case.get("name")]))
        if case.find("failure") is not None:
            counts.failed += 1
            counts.failed_names.append(name)
        elif case.find("error") is not None:
            counts.errors += 1
            counts.failed_names.append(name)
        elif case.find("skipped") is not None:
            counts.skipped += 1
        else:
            counts.passed += 1
    return counts


@dataclass
class Summary:
    status: str
    detail: str
    counts: TestCounts | None
    report_note: str | None


def classify(job_result: str, setup_outcome: str, tests_outcome: str,
             counts: TestCounts | None, report_problem: str | None = None) -> Summary:
    """Decide what happened, keeping 'assertions failed' apart from 'tests never ran'."""
    job_result, setup_outcome, tests_outcome = (v.strip().lower() for v in (job_result, setup_outcome, tests_outcome))
    tests_ran = tests_outcome in ("success", "failure") or (not tests_outcome and counts is not None)

    if not tests_ran:
        if job_result == "cancelled" or "cancelled" in (setup_outcome, tests_outcome):
            return Summary(CANCELLED, "The run was cancelled before the tests ran.", None, "Tests did not run.")
        if setup_outcome == "failure":
            where = "the setup / build step failed"
        elif job_result in ("", "skipped"):
            where = "the test job did not start (a dependency or the runner failed)"
        else:
            where = f"the test job ended with '{job_result}' before the test step"
        return Summary(PIPELINE_FAILED, f"Tests did not run: {where}.", None, "Tests did not run, so there is no test report.")

    failures_in_report = counts is not None and (counts.failed or counts.errors)
    if failures_in_report:
        return Summary(TESTS_FAILED, "One or more tests failed.", counts, None)
    if tests_outcome == "failure":
        note = (f"Test report could not be read: {report_problem}." if report_problem
                else "No test report found; counts unavailable.")
        return Summary(TESTS_FAILED, "The test step failed, but no failures could be read from a report "
                       "(possible crash, collection error or timeout).", counts, note)
    if job_result == "failure":
        return Summary(PIPELINE_FAILED, "Tests passed, but a later pipeline step failed.", counts,
                       None if counts else "No test report found; counts unavailable.")
    if job_result == "cancelled":
        return Summary(CANCELLED, "The run was cancelled after the tests.", counts, None)
    note = None
    if counts is None:
        note = f"Test report could not be read: {report_problem}." if report_problem else "No test report found; counts unavailable."
    return Summary(PASSED, "All tests passed.", counts, note)


def format_counts(counts: TestCounts) -> str:
    failed = counts.failed + counts.errors
    text = f"{counts.passed} passed, {failed} failed, {counts.skipped} skipped ({counts.total} total)"
    if counts.errors:
        text += f"; {counts.errors} of the failures are errors"
    return text


def build_message(env: Mapping[str, str]) -> str:
    report_path = env.get("CI_REPORT_PATH", "reports/junit.xml")
    report_problem = None
    try:
        counts = parse_junit(report_path)
    except ReportError as exc:
        counts, report_problem = None, str(exc)
        log.warning("Could not read test report %s: %s", report_path, exc)

    summary = classify(env.get("CI_JOB_RESULT", ""), env.get("CI_SETUP_OUTCOME", ""),
                       env.get("CI_TESTS_OUTCOME", ""), counts, report_problem)

    demo = env.get("CI_DEMO", "").lower() == "true"
    repo = env.get("GITHUB_REPOSITORY", "(unknown repository)")
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = env.get("GITHUB_RUN_ID")
    run_url = f"{server}/{repo}/actions/runs/{run_id}" if run_id else "(not running in GitHub Actions)"
    if run_id and env.get("GITHUB_RUN_ATTEMPT", "1") not in ("", "1"):
        run_url += f"/attempts/{env['GITHUB_RUN_ATTEMPT']}"

    suite = env.get("CI_SUITE") or "Test suite"
    job = env.get("CI_JOB")
    lines = []
    if demo:
        lines.append(f"[DEMO] Simulated scenario: {env.get('CI_SCENARIO') or 'n/a'}. Not a real project result.")
    lines += [
        f"{'[DEMO] ' if demo else ''}{HEADLINES[summary.status]}",
        "",
        f"Repository: {repo}",
        f"Workflow: {env.get('GITHUB_WORKFLOW', 'n/a')}",
        f"Suite / job: {suite}" + (f" / {job}" if job else ""),
        f"Branch: {env.get('GITHUB_REF_NAME', 'n/a')}",
        f"Result: {summary.detail}",
    ]
    if summary.counts is not None:
        lines.append(f"Tests: {format_counts(summary.counts)}")
        if summary.counts.failed_names:
            lines.append("Failed tests:")
            names = summary.counts.failed_names
            lines += [f" • {n}" for n in names[:MAX_FAILED_NAMES]]
            if len(names) > MAX_FAILED_NAMES:
                lines.append(f" • … and {len(names) - MAX_FAILED_NAMES} more")
    if summary.report_note:
        lines.append(f"Tests: {summary.report_note}")
    lines.append(f"Run: {run_url}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_output()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(prog="python -m notifier.ci_summary", description=__doc__.splitlines()[0])
    parser.add_argument("--preview", action="store_true", help="print the message instead of sending it")
    args = parser.parse_args(argv)
    load_dotenv()
    return deliver(build_message(os.environ), args.preview)


if __name__ == "__main__":
    sys.exit(main())
