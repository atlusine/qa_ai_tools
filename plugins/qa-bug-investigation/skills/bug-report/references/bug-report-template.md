# Bug Report Templates

## Default: Markdown

```markdown
# [Area] <What goes wrong> when <condition>

| Field | Value |
|-------|-------|
| Priority | High / Medium / Low |
| Reproducibility | Always / Intermittent (x of y) / Once |
| Environment | URL, build/version, browser + version, OS, device |
| User / role | Guest / customer / admin … |
| Related | TC-xxx, AC-xx, JIRA-123 |

## Preconditions
- …

## Steps to reproduce
1. …
2. …

## Expected result
… (source: AC-xx / TC-xxx / spec)

## Actual result
…

## Screenshots
| # | File | Step | Shows |
|---|------|------|-------|
| 1 | `area-01-before.png` | Step 1 | … |
| 2 | `area-02-actual.png` | Step 2 | Actual result: … |

![Actual result](area-02-actual.png)

## Logs
- Console:
  ```
  <verbatim error lines>
  ```
- Network: `GET /api/... → 500` — response excerpt:
  ```json
  { ... }
  ```

## Scope / variations
| Variation | Reproduces? |
|-----------|-------------|
| Chrome 1xx, guest | Yes |
| Firefox 1xx, guest | Not checked |

## Notes
- Hypothesis (unverified): …

## Open questions / assumptions
- …
```

- **Screenshots** is mandatory and has at least the actual-result screenshot.
- Omit **Logs** when there are none, and **Scope / variations** when no variations were tried.
- Write "Not checked" rather than guessing a variation's result.

## Jira

Map the report onto Jira fields:

| Jira field | Content |
|------------|---------|
| Issue type | Bug |
| Summary | The title |
| Priority | Priority from the guide |
| Labels | `bug`, area label, e.g. `search` |
| Environment | Environment line (or put it in the description if the field is not on the screen) |
| Attachments | All screenshots (required) |
| Description | Everything else below, in Markdown |
| Links | "relates to" the test-case / story issue; "duplicates" if applicable |

Description body:

```markdown
**Reproducibility:** Always · **Role:** Guest

## Preconditions
…

## Steps to reproduce
1. …

## Expected result
… (source: …)

## Actual result
…

## Screenshots
1. `area-01-before.png` — Step 1: …
2. `area-02-actual.png` — Step 2, actual result: …

## Logs
…

## Notes
…
```

Attach the screenshot files to the issue and refer to them by file name — never link local file paths.

## Short (chat / Slack)

```
🐞 [Area] <what goes wrong> when <condition>
Env: <url>, <browser>  ·  Priority: <x>  ·  Repro: Always
Steps: 1) … 2) … 3) …
Expected: …  |  Actual: …
Screenshot: <attached file>
```
