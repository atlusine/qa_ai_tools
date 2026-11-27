---
name: qa-core
description: "TODO: the shared QA engineering foundation that every tester agent in this plugin applies before its specific testing approach: workflow, test-design basics, evidence, defect handoff and reporting."
---

# QA Core

The foundation shared by every testing approach in this plugin. Each tester agent
loads this skill **and** one approach skill. This skill says *how a QA engineer
works*; the approach skill says *what is special about this type of testing*.

## Principles

TODO: core QA principles (risk-based, independent, evidence over opinion, ...).

## Workflow

TODO: the steps every approach follows:

1. Understand: requirement, scope, risks, open questions
2. Plan: what to test, what not to test, environment, data, entry/exit criteria
3. Design: test conditions → test cases (see `qa-test-design:manual-test-cases`)
4. Execute: run, observe, record results
5. Evidence: screenshots, logs, requests/responses, exact error text
6. Report: results summary, defects, coverage, risks

## Test design basics

TODO: EP, BVA, decision tables, state transition, error guessing (short version or a link).

## Severity and priority

TODO: shared definitions, consistent with the `bug-report` skill.

## Defect handoff

TODO: when and how to hand a finding to `bug-report`. Never create a bug without the user's explicit approval.

## Reporting

TODO: the common test-report format. See `references/test-report-template.md`.

## Rules for all approaches

TODO: no invented data, state assumptions, one check per test case, concrete test data, ...
