---
name: qm-release-todo-pick
description: Daily: pick one open "To Do for Release" issue on the waveware GitLab QM board and open a draft merge request for it.
---

Daily check of the QM release to-dos on GitLab: pick one issue and open a draft merge request for it in the same repo. Only the actions listed below are allowed: create one branch, create one draft MR. Do NOT edit, comment on, assign, close or merge anything else.

Source
- GitLab project: waveware/waveware (URL-encoded id: waveware%2Fwaveware)
- Board: https://gitlab.com/waveware/waveware/-/boards/8891742 (board id 8891742)
- Auth: a GitLab personal access token with the "api" scope in the user environment variable GITLAB_TOKEN. Read it in PowerShell with [Environment]::GetEnvironmentVariable('GITLAB_TOKEN','User') if $env:GITLAB_TOKEN is empty. Never print the token. If it is missing, stop and report: "GITLAB_TOKEN is not set – create an api-scope token at https://gitlab.com/-/user_settings/personal_access_tokens and set it as a user environment variable." If a write call returns 403 (token only has read_api), still do steps 1-3 and report that the MR could not be created because the token lacks the api scope.

All calls: PowerShell Invoke-RestMethod, header PRIVATE-TOKEN, base https://gitlab.com/api/v4.

1. GET /projects/waveware%2Fwaveware/boards/8891742 and read its lists. Find the list whose label name matches "to do for release" (case-insensitive; also accept close variants such as "ToDo::Release", "To Do - Release", "Release To Do"). If none matches, report all list/label names and stop.
2. GET /projects/waveware%2Fwaveware/issues?labels=<label, URL-encoded>&state=opened&per_page=100 (follow pagination).
3. Rank the issues: unassigned before assigned; then priority/severity label (priority::1 / P1 / critical / high first); then earliest due date, then earliest milestone due date; then oldest created_at. Skip issues labelled "blocked" unless nothing else is left.
4. Skip issues that already have work: for each candidate in rank order, GET /projects/waveware%2Fwaveware/issues/<iid>/related_merge_requests and GET /projects/waveware%2Fwaveware/repository/branches?search=<iid>-. If it has an open MR or a branch starting with "<iid>-", move to the next candidate. The first candidate without either is today's pick. If every candidate already has work, report that and stop (create nothing).
5. Create the branch: GET /projects/waveware%2Fwaveware to read default_branch. Branch name = "<iid>-<title slug>" (lowercase, non-alphanumerics -> "-", collapse repeats, max 50 chars total). POST /projects/waveware%2Fwaveware/repository/branches with branch=<name>&ref=<default_branch>.
6. Create the MR: GET /user for the token owner's id. POST /projects/waveware%2Fwaveware/merge_requests with JSON body: source_branch=<name>, target_branch=<default_branch>, title="Draft: Resolve \"<issue title>\"", description="Closes #<iid>\n\nAuto-created by the daily QM release to-do pick.", assignee_id=<user id>, remove_source_branch=true. Do this only once per run.
7. Report:
   **QM release to-dos – <today's date>**: <N> open
   **Today's pick:** #<iid> <title> – <issue web_url>
   Why: <one line: which rule decided it>
   **Draft MR created:** !<mr iid> – <mr web_url> (branch <name>)  — or the reason it was not created
   **Other open release to-dos** (table: #iid, title, assignee, due date, has MR?), max 15 rows, same order.