# Bug Report Template (Jira)

Every bug report uses this format. It is written in Jira wiki markup so it can be pasted into a Jira ticket as is.

## Jira fields

| Field | Value |
|-------|-------|
| Issue Type | Bug |
| Summary | `[<FE/BE/UI>] <Area/Page>: <what goes wrong> when <condition>` |
| Severity | Critical / Major / Minor / Trivial |

## Description

```
h3. Environment
* *OS:* <OS and version>
* *Browser / App:* <browser and version, or app and version>
* *Device:* <desktop / device model>
* *Environment:* <dev / staging / prod>
* *URL:* <page URL>
* *User role:* <role or account type>

h3. Preconditions
* <state needed before step 1: logged in/out, existing data, settings>

h3. Steps to Reproduce
# <action with concrete data>
# <action>
# <action>

h3. Expected Result
<what should happen> _(Source: <requirement / acceptance criterion / common sense>)_

h3. Actual Result
<what actually happens>
{code}
<exact error message, status code or log line, if any>
{code}

h3. Severity
<Critical / Major / Minor / Trivial> — <one-line reason>

h3. Attachments
* <screenshot / video / log file names, or "None">
```

## Jira markup cheat sheet

| Markup | Result |
|--------|--------|
| `h3. Title` | Heading |
| `* item` | Bullet list |
| `# item` | Numbered list (steps) |
| `*text*` | Bold |
| `_text_` | Italic |
| `{code}...{code}` | Code block for errors and logs |
| `{{text}}` | Inline monospace, e.g. field values like `{{test@mail}}` |

## Rules

- Leave out a section only if it truly does not apply (e.g. **Preconditions** when the bug starts from the home page logged out). Never leave placeholders like `<...>` in the final report.
- If the bug is created through a Jira tool that expects Markdown instead of wiki markup, keep the same sections and order and convert the markup (`h3.` → `###`, `#` → `1.`, `{code}` → triple backticks).
