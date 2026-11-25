---
name: bug-report
description: Report bugs in Jira or artifacts from test notes or artifacts. Use when the user asks to report, log or file a bug.
---

## Inputs
Work from whatever the user gives: a test case, a test run, a test plan, a test session, a test report, a defect report, a screenshot or a plain description. If something that changes the bug report is missing (steps to reproduce, expected vs actual, environment), list it under **Open questions** instead of guessing — do not block on it.

# Check for duplicates
Search the project's Jira for similar defects by error message, feature and key symptoms, including closed ones. 
List any matches with key, status and why they match. If there's a likely duplicate, suggest commenting on it instead of filing a new bug.
If Jira isn't accessible or the project is unknown, say the check was not done.

# Bug Report
1. Write a title
2. Write numbered steps to reproduce
3. Add Expected vs Actual
4. Add app version, if not available set Unknown
5. Add browser version for web applications
6. Add OS and mention bitness
7. Attach screenshots, videos, logs, or other artifacts. remove passwords, tokens and personal data from logs and screenshots before attaching them.
8. Mention the related test case
9. Set priority and severity
10. Use template.md for the format


## Output
Create an artifact which contains the bug report details. Ask the user if they want to file the bug report in Jira. If user approves create an issue in Jira and write the issue link in Claude. 

