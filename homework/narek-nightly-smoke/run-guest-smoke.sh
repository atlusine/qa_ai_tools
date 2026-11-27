#!/usr/bin/env bash
# Nightly guest smoke: runs the guest-only smoke specs of toolshop-automation
# and writes everything for one run into runs/<YYYY-MM-DD_HHMMSS>[_label]/ next to this script.
#
# Deterministic part of the workflow (no AI): run tests, collect artifacts,
# write a compact summary.json the triage step can read cheaply.
#
# Usage:  bash homework/narek-nightly-smoke/run-guest-smoke.sh   # public site
#         RUN_LABEL=forced-red BASE_URL=http://localhost:9 bash .../run-guest-smoke.sh   # forced-red demo
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEWORK_DIR="${FRAMEWORK_DIR:-$SCRIPT_DIR/../../toolshop-automation}"
RUNS_DIR="${RUNS_DIR:-$SCRIPT_DIR/runs}"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
# Optional RUN_LABEL (e.g. forced-red) is added to the folder name; seconds keep runs unique.
RUN_DIR="$RUNS_DIR/${STAMP}${RUN_LABEL:+_$RUN_LABEL}"
mkdir -p "$RUN_DIR"

cd "$FRAMEWORK_DIR" || { echo "framework not found: $FRAMEWORK_DIR"; exit 2; }

# Guest specs only: no login, no password, no shared account (TC01 is skipped on purpose).
SPECS="tests/smoke/smoke_test_guest_"

{
  echo "started=$(date -Iseconds)"
  echo "base_url=${BASE_URL:-https://practicesoftwaretesting.com}"
  echo "framework_commit=$(git rev-parse --short HEAD 2>/dev/null)"
  echo "specs=$SPECS*"
  echo "not_covered=TC01 customer login (public site shows a Cloudflare bot check on login)"
} > "$RUN_DIR/run-info.txt"

PLAYWRIGHT_JSON_OUTPUT_NAME="$RUN_DIR/results.json" \
  npx playwright test "$SPECS" \
    --reporter=list,json \
    --output="$RUN_DIR/artifacts" \
    > "$RUN_DIR/console.log" 2>&1
EXIT_CODE=$?
echo "exit_code=$EXIT_CODE" >> "$RUN_DIR/run-info.txt"

# Compact summary: one entry per test, last attempt's status, every attempt's
# first error line, artifact paths, and a hint if a bot-check page was captured.
node - "$RUN_DIR" <<'NODE'
const fs = require("fs");
const path = require("path");
const runDir = process.argv[2];
let report;
try {
  report = JSON.parse(fs.readFileSync(path.join(runDir, "results.json"), "utf8"));
} catch (e) {
  fs.writeFileSync(path.join(runDir, "summary.json"),
    JSON.stringify({ error: "results.json missing or unreadable: " + e.message }, null, 2));
  process.exit(0);
}
const tests = [];
const walk = (suite, file) => {
  for (const spec of suite.specs || []) {
    for (const t of spec.tests || []) {
      const attempts = (t.results || []).map((r) => {
        const attachments = (r.attachments || []).filter((a) => a.path).map((a) => a.path);
        const ctx = attachments.find((p) => p.endsWith("error-context.md"));
        let botCheck = false;
        if (ctx && fs.existsSync(ctx)) {
          botCheck = /security verification|verify you are human|cloudflare/i.test(fs.readFileSync(ctx, "utf8"));
        }
        return {
          retry: r.retry,
          status: r.status,
          durationMs: r.duration,
          error: r.error ? String(r.error.message || "").replace(/\u001b\[[0-9;]*m/g, "").split("\n").slice(0, 4).join(" | ") : null,
          attachments,
          botCheckPage: botCheck,
        };
      });
      tests.push({
        title: spec.title,
        tcId: (spec.title.match(/TC\d+/) || [null])[0],
        file: path.join("tests", file || suite.file || ""),
        line: spec.line,
        outcome: t.status, // expected | unexpected | flaky | skipped
        attempts,
      });
    }
  }
  for (const s of suite.suites || []) walk(s, s.file || file);
};
for (const s of report.suites || []) walk(s, s.file);
const stats = report.stats || {};
fs.writeFileSync(path.join(runDir, "summary.json"), JSON.stringify({
  passed: tests.filter((t) => t.outcome === "expected").length,
  failed: tests.filter((t) => t.outcome === "unexpected").length,
  flaky: tests.filter((t) => t.outcome === "flaky").length,
  skipped: tests.filter((t) => t.outcome === "skipped").length,
  durationMs: stats.duration,
  tests,
}, null, 2));
NODE

echo "run_dir=$RUN_DIR"
echo "exit_code=$EXIT_CODE"
exit 0
