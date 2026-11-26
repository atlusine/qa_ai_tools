# tests/: spec layer

Loaded when you work on a spec. The repo-wide rules still apply; this is the spec-specific detail.

## Placement

| The test…                                                     | Folder              | Tag           | File name                                  |
| ------------------------------------------------------------- | ------------------- | ------------- | ------------------------------------------ |
| is a core journey a release can't ship without                 | `tests/smoke/`      | `@smoke`      | `smoke_test_<actor>_<feature>.spec.js`     |
| is everything else                                            | `tests/regression/` | `@regression` | `regression_test_<actor>_<feature>.spec.js` |

`<actor>` is `guest`, `customer` or `admin`. Keep smoke small (under 10 tests, under a minute); it's what runs first.

## A spec reads like a test case

Only these appear in a spec: imports, `test.describe`, `beforeAll` test data, `new <PageObject>(page)`, and `await <object>.<verb>_…()` calls. No `expect`, no locators, no `page.goto`, no literals for accounts or UI text. The `validate-edit` hook flags each of these as you write.

## Test IDs

Each test title starts with the next free `TC<nn>`. Check before picking one:

```bash
grep -rhoE 'TC[0-9]+' tests | sort -u | tail -3
```

Add the new row to the *Implemented test cases* table in `CLAUDE.md`.
