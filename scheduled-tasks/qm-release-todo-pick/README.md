# Sample scheduled task: QM daily release to-do pick

A Claude Code desktop **scheduled task** that runs every day at 08:00 and:

1. Reads the QM board on GitLab (`waveware/waveware`, board `8891742`).
2. Lists open issues in the **"To Do for Release"** column.
3. Picks one issue: unassigned first, then priority label, then due date, then oldest. Skips `blocked` and issues that already have a branch or MR.
4. Creates a branch `<iid>-<title-slug>` and opens a **draft** merge request (`Closes #<iid>`), assigned to the token owner.
5. Reports the pick, the MR link, and the remaining release to-dos.

## Setup

1. Create a GitLab personal access token with the `api` scope (use `read_api` if you only want the report, without the MR).
2. Store it as a user environment variable. Never commit the token:
   ```powershell
   [Environment]::SetEnvironmentVariable('GITLAB_TOKEN','<your-token>','User')
   ```
3. Copy `SKILL.md` to `%USERPROFILE%\.claude\scheduled-tasks\qm-release-todo-pick\SKILL.md`, or ask Claude in the desktop app to create a scheduled task from it (cron `0 8 * * *`).
4. Restart the Claude app, then click **Run now** on the task once to approve the tools it needs.

The task runs only while the Claude desktop app is open; a missed run starts on the next launch.

To use it for another project, change the project path and board id in `SKILL.md`.
