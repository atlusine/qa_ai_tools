---
name: bug-report
description: Report bugs in Jira or artifacts baised on test notes or artifacts. Use when the user asks to report, log or file a bug. 
---

## Inputs
Work from whatever the user gives: a test case, a test run, a test plan, a test session, a test report, an artifat file,  a defect report, a screenshot or a plain description. If something that changes the bug report is missing (steps to reproduce, expected vs actual, environment), list it under **Open questions** instead of guessing — do not block on it.

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
9. Set priority and severity to High for crashes and unexpected errors, Medium for functional issues, and Low for cosmetic issues.



## Process
2. **Check for duplicates** in Jira before writing anything (see **Check for duplicates**).
3. **Gather the details:** steps to reproduce, expected vs actual, environment (app version, browser, OS and bitness) and artifacts. Note anything missing under **Open questions**.
4. **Write the bug report** following the steps in **Bug Report** 
5. **Review** before presenting:
   - Someone who didn't find the bug can reproduce it from the steps alone
   - The title describes the symptom and where it happens
   - Expected and actual results are specific and verifiable
   - Logs and screenshots contain no passwords, tokens or personal data
   - Priority and severity are set and justified
6. **Deliver** the report as described in **Output**, and file it in Jira only after the user approves.

## Output
Create an artifact which contains the bug report details. Ask the user if they want to file the bug report in Jira. If user approves create an issue in Jira and write the issue link in Claude. 

