# Severity and Priority

**Severity = how bad it is for the user. Priority = how soon it should be fixed.** They're set separately, and each gets a one-line reason.

## Severity

| Level | Use when | Example |
|---|---|---|
| Critical | Data loss, money lost, security hole, or the main flow is impossible for everyone | Every order fails at checkout |
| High | A core feature gives wrong results or hides failures; no reasonable workaround | A server error is shown as "There are no products found." |
| Medium | A feature is partly wrong; a workaround exists or only some inputs are affected | Searching text in the middle of a word finds nothing |
| Low | Cosmetic, usability, rare input, or behaviour the spec doesn't define | The search box is emptied after each search |

## Priority

| Level | Use when |
|---|---|
| Highest | Blocks a release or many users right now |
| High | Breaks a written requirement on a core flow (even if severity is Medium) |
| Medium | Should be fixed this cycle |
| Low | Nice to fix, or waiting for a product decision |

## Rules of thumb
- **The spec is silent** → mark the expected result as an assumption, ask the PO, and set priority Low.
- **Intermittent** → severity as if it always happened, but state how often it happens.
- **Mocked failure** (fake 500, aborted request) → severity is about what users would see during a real outage. Add any real-world sighting.
- **Security** (data of other users visible, script runs, login bypass) → at least High, and keep the details out of public comments.
