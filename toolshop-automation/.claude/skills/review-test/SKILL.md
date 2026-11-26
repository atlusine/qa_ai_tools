---
name: review-test
description: Pre-commit / pre-PR review of a toolshop-automation change — runs the review-diff grep gate, then checks what a grep cannot (independence, vacuous assertions, grounding, flakiness proof, titles) and reports findings as blocking / advisory with file:line. Load before committing, opening a PR, or when asked to review a test change.
---

# Review a test change

## 1. Run the automated gate

```bash
bash scripts/claude-hooks/review-diff.sh          # added lines vs main, untracked files included
```

Every **BLOCK** must be fixed. Every **ADVISE** must be removed or justified in the PR description.

## 2. Run the tests

```bash
npx playwright test --retries=0                                   # whole suite, parallel
npx playwright test <changed specs> --retries=0 --repeat-each=5   # flake proof
```

A change that hasn't been run is not reviewed. Say so if you couldn't run it.

## 3. Answer what the gate can't see

1. **Independence.** Can each new test run alone, first, last, or in parallel with itself? Does it rely on a cart, login, or data created by another test?
2. **Vacuous assertions.** Could any `assert_*` pass when the page didn't load? Absence checks need a present-anchor first. "Every item matches" checks need `length > 0`.
3. **Grounding.** Is each new `data-test` value and message string actually present in the live app (spot-check with the Playwright MCP snapshot)? Is any one invented?
4. **Right signal.** Does each action wait on the response that changes state, captured **before** the action?
5. **Shared-site safety.** Does anything change a demo account's data, or try wrong passwords on one?
6. **Invariants.** Does any assertion depend on exact counts or specific products that the shared data could change?
7. **Titles.** Read each title as someone who hasn't opened the spec: action → expected outcome, with a `TC<nn>` id, 85 characters or fewer.
8. **Bookkeeping.** New row in the `CLAUDE.md` test case table? New selectors named `<area><Element><Type>`?

## 4. Report

Findings most severe first, each with `file:line`, split into **Blocking**, **Advisory (justify in the PR)** and **Pre-existing (don't fix here)**. State what you verified by running vs. by reading. Don't pad the list.
