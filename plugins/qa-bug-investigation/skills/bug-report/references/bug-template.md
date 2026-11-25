# Bug Report Templates

## Default: bug (Jira markdown)

Title: `[<Area>] <What is wrong> (<exact data>)`

```markdown
**Severity:** <Critical | High | Medium | Low> (<one-line impact on the user>)
**Priority:** <Highest | High | Medium | Low> (<one-line reason>)
**Breaks:** <requirement / AC id and quoted text> (<epic or story key>)

### Environment
* URL: <url> (<app version or build, if shown>)
* Browser / device: <browser + version, OS, viewport if relevant>
* User: <guest / role / test account name — never a password>
* Date: <YYYY-MM-DD, time with time zone>

### Preconditions
<state needed before step 1: logged in or not, data that must exist, page open>

### Steps to reproduce
1. <one action, exact data in `code`>
2. <one action>

### Expected result
<what the requirement says, quoted where possible>

### Actual result
<exact on-screen text in quotes; what is shown or missing>

### More examples (same cause)
| Input | Expected | Actual |
| --- | --- | --- |
| `...` | ... | ... |

### Likely cause / notes
<pattern: when it fails and when it works; API result for the same input; "mocked" if a fake response was used>

### Reproducibility
<Always | Intermittent>: <N of N> <manual / automated> runs (<test IDs if any>)

### Evidence
<screenshot file names, console errors, failed request: METHOD URL → status + body>
```

## Comment on an existing ticket

```markdown
Confirmed on <date> (<how>, <N of N> runs): <one line>.
**New information:** <what the ticket doesn't say yet: steps, boundary, pattern, other inputs>.
Steps: 1) … 2) …
Evidence: <files>. Tests: <IDs>.
```

## Reproduction-only answer

```
Verdict: REPRODUCED | INTERMITTENT (x of y) | NOT REPRODUCED
Runs: <N of N>, <date/time>, <browser>
What happened: <one or two lines, exact on-screen text>
Evidence: <screenshots>, <console errors>, <failed API calls with status>
```
