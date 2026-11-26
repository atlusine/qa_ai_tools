---
name: analyze-failure
description: Diagnosing a failing or flaky Playwright test in toolshop-automation — reading the error, screenshot, video and trace, classifying the failure as product bug, test bug, race, shared-data drift or environment, and fixing the cause instead of adding retries or waits. Load when a spec fails, flakes, times out, or passes locally and fails in CI.
---

# Analyze a failure

**A retry that makes a test pass hasn't fixed anything; it has hidden the diagnosis.** Your value here is the classification, not the patch.

## 1. Collect the evidence. Read it before theorizing

```bash
npx playwright test -g "<TC id or title>" --retries=0 --reporter=list
ls -t test-results/ | head
npx playwright show-trace test-results/<dir>/trace.zip    # step-by-step DOM, network, console
```

Each failed test leaves `test-failed-1.png`, `video.webm`, `trace.zip` and `error-context.md` (an ARIA snapshot of the page at the moment of failure) in `test-results/<dir>/`. **Read `error-context.md` and the screenshot first.** They usually settle product bug vs. test bug at a glance.

Read the error text **verbatim**. Playwright names the locator, the expected and received values, and the call log.

## 2. Classify. This is the whole job

| Symptom                                                         | Almost always                                     | Where to look                                         |
| --------------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| `strict mode violation: … resolved to N elements`               | Test bug: locator not scoped                      | Use `.first()`, or scope to a row or card             |
| `page.goto: Timeout … waiting until "load"`                     | Test bug: wrong navigation                        | Use `PlaywrightMethods.open_url`                      |
| `Expected: 42.45 Received: 14.15` right after an action         | Race: one-shot read before the re-render          | Replace with `toHaveText` / `expect.poll`             |
| `waitForResponse` timeout                                       | The action never fired, or the endpoint or method is wrong | **Upstream** of the wait: was the click done? `QUERY` vs `GET`? |
| Passes alone, fails under `fullyParallel`                       | Shared state                                      | Same logged-in account used by two tests              |
| Different step fails each run                                   | Genuine race                                      | The signal that actually gates the step               |
| Same step every time, screenshot shows wrong data or an error   | **Product bug**                                   | Reproduce by hand in the browser, then report it      |
| Assertion on a count or specific product fails                  | Shared-data drift                                 | Assert an invariant instead                           |
| Everything red from the first test                              | Environment                                       | Is the site up? `session-context.sh` prints reachability |

## 3. Check the two state questions

- Does it pass alone (`--workers=1 -g TC..`) but fail in the full run? → shared state.
- Does it pass once but fail on `--repeat-each=5`? → leftover state, or a race.

## 4. Fix the cause, not the symptom

Forbidden as a fix: raising `retries`, adding `waitForTimeout`, `force: true`, or loosening an assertion so it accepts the wrong value.

**If it's a product bug, stop.** Mark the test `test.fixme` with the issue URL in a comment directly above it, and write the report with the `bug-report` skill (`qa-bug-investigation` plugin). Include the screenshot, the trace, and the exact expected vs. actual.

## 5. Report

Category, the evidence for it (quoted error, screenshot observation, trace step), the fix, and whether you **verified it by running** (`--repeat-each=5`, green) or only inferred it from reading. If you couldn't reproduce it, say so plainly.
