# Test Report Template

Every testing session ends with this report. Fill every section; write "None" instead of
leaving one out. No `<...>` placeholders in the final report.

```markdown
## Test report: <ticket key> <short title>

**Tested by:** <name> · **Date:** <YYYY-MM-DD> · **Testing type:** <API / smoke / UAT / exploratory>

### Scope
- **In scope:** <what was tested>
- **Out of scope:** <what was not tested, and why>

### Environment
- **URL:** <app / API URL>
- **Build / version:** <version, or "unknown">
- **Browser / device:** <browser and version, device>
- **Accounts / roles:** <role names, never passwords>

### Results summary

| Passed | Failed | Blocked | Not run | Total |
|--------|--------|---------|---------|-------|
| <n>    | <n>    | <n>     | <n>     | <n>   |

### Results per case

| ID | Title | Status | Evidence / bug |
|----|-------|--------|----------------|
| <ID> | <title> | Passed / Failed / Blocked / Not run | <file name, or bug key> |

### Defects found

| Bug | Title | Severity |
|-----|-------|----------|
| <key> | <title> | <severity> |

### Risks and open questions
- <what could still go wrong, what is unclear>

### Recommendation
<Ready / Ready with known issues / Not ready> — <one-line reason>
```

## Rules

- Counts in the summary must match the per-case table.
- Each Failed case links a bug key, or says "bug pending approval".
- Each Blocked case says what blocks it.
- The recommendation is based on the open defects and the High-priority results, not on the pass rate alone.
