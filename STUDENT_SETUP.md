# Student Setup Guide

Follow these steps once before the first lesson. When you're done, you can write test cases from Jira tickets and run them in a real browser with Claude Code.

Plan for about 30 minutes and a 300 MB download.

- [Before you start](#before-you-start)
- [Step 1: Install Node.js](#step-1-install-nodejs)
- [Step 2: Install Claude Code and log in](#step-2-install-claude-code-and-log-in)
- [Step 3: Add the course plugins](#step-3-add-the-course-plugins)
- [Step 4: Turn on the Playwright browser plugin](#step-4-turn-on-the-playwright-browser-plugin)
- [Step 5: Connect Jira](#step-5-connect-jira)
- [Check your setup](#check-your-setup)
- [Optional: Playwright test project with video](#optional-playwright-test-project-with-video)
- [Troubleshooting](#troubleshooting)

## Before you start

| What | Why you need it | Notes |
|------|-----------------|-------|
| Windows 10+, macOS 12+ or Linux (Ubuntu 20.04+) | Runs Claude Code and the test browser | About 1 GB free disk space |
| Internet connection | Downloads the tools and the browser | About 300 MB in total |
| A Claude account with Claude Code access | Claude Code needs it to log in | A paid plan (Pro, Max, Team or Enterprise) or a Claude Console account |
| Access to the course Jira site | Reading tickets and saving test cases | Your teacher sends an invite to your email. Accept it before Step 5 |
| A terminal | You type the install commands here | Windows: PowerShell · macOS and Linux: Terminal |

On a school or work computer, ask IT first whether you're allowed to install software.

The practice website for all lessons is [practicesoftwaretesting.com](https://practicesoftwaretesting.com/). It's public and shared by everyone, so products, accounts and orders may change while you work.

## Step 1: Install Node.js

Node.js runs the Playwright browser tools. You need version 18 or newer.

1. Go to [nodejs.org](https://nodejs.org/) and download the **LTS** version for your system.
2. Run the installer and accept the defaults.
3. Close your terminal and open a new one.
4. Check the installation:

   ```bash
   node -v
   npx -v
   ```

   You should see a version number for each, for example `v20.10.0`.

## Step 2: Install Claude Code and log in

Run the command for your system in a terminal.

**macOS or Linux:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

If those don't work on your computer, use npm instead (Node.js is already installed):

```bash
npm install -g @anthropic-ai/claude-code
```

Then start Claude Code and log in:

1. Type `claude` and press Enter.
2. Choose to log in with your Claude account. A browser window opens.
3. Approve the login in the browser, then go back to the terminal.
4. Type `/status` to confirm you're logged in.

If the [Claude Code setup docs](https://docs.claude.com/en/docs/claude-code/setup) show different commands, follow the docs: they are the most up to date.

## Step 3: Add the course plugins

The course plugins live in this repository. Inside Claude Code, run:

```
/plugin marketplace add atlusine/qa_ai_tools
/plugin install qa-test-design@qa-ai-tools
```

If you cloned the repository to your computer, you can add it from the folder instead:

```
/plugin marketplace add /path/to/qa_ai_tools
/plugin install qa-test-design@qa-ai-tools
```

Restart Claude Code after installing (type `/exit`, then `claude` again).

New plugins are added during the course (bug investigation, automation). When your teacher announces one, run `/plugin marketplace update qa-ai-tools` and install it the same way.

## Step 4: Turn on the Playwright browser plugin

The Playwright plugin lets Claude open a browser, click, type and take screenshots.

1. In Claude Code, type `/plugin`.
2. Open the **Discover** tab and search for `playwright`.
3. Install the Playwright plugin and restart Claude Code.

You don't need to install Playwright separately. It downloads itself the first time Claude uses the browser.

If the first browser test says the browser isn't installed, run this once in a terminal:

```bash
npx playwright install chromium
```

## Step 5: Connect Jira

Claude reads and writes Jira tickets through the Atlassian connector on your Claude account.

1. Accept the Jira invite from your teacher and check that you can open the course project in your browser.
2. Go to [claude.ai](https://claude.ai) → **Settings** → **Connectors**.
3. Find **Atlassian** and click **Connect**. Log in with the same Atlassian account that has access to the course Jira.
4. Restart Claude Code. Type `/mcp` and check that the Atlassian server is listed as connected.

## Check your setup

Do this short test run. If every step works, you're ready for the lesson.

1. Open a terminal in any empty folder and type `claude`.
2. Ask: `What skills do you have for test design?` Claude should mention `manual-test-cases`.
3. Ask: `Open https://practicesoftwaretesting.com/ with Playwright, search for "pliers" and tell me how many products are found.` A browser runs, and Claude should answer **4 products**.
4. Ask: `Show me the summary of Jira ticket <a ticket key from your teacher>.` Claude should show the ticket's title.

If a step fails, check [Troubleshooting](#troubleshooting) or ask your teacher.

## Optional: Playwright test project with video

You need this only for the automation lessons. It creates a test project that records a video for every failed test.

```bash
mkdir toolshop-tests
cd toolshop-tests
npm init playwright@latest
```

Answer the questions (the defaults are fine). Then open `playwright.config.ts` and set these options inside `use`:

```ts
use: {
  video: 'retain-on-failure',      // keep a video only for failed tests
  screenshot: 'only-on-failure',
  trace: 'retain-on-failure',      // step-by-step replay of failed tests
},
```

Run the tests and open the report:

```bash
npx playwright test
npx playwright show-report
```

Videos of failed tests are saved as `.webm` files in the `test-results/` folder and are shown in the report.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `node` or `claude`: "command not found" | Close the terminal and open a new one. If it still fails, reinstall and make sure the installer adds it to your PATH |
| Windows: "running scripts is disabled on this system" | Run PowerShell as administrator once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `npm install -g` fails with a permission error (macOS/Linux) | Use the `curl` installer from Step 2 instead of npm |
| `/plugin marketplace add` fails | Check the spelling `atlusine/qa_ai_tools`, and that you're connected to the internet. Or clone the repository and add it from the folder |
| The browser doesn't start ("Executable doesn't exist") | Run `npx playwright install chromium` |
| Linux: browser fails with missing libraries | Run `npx playwright install --with-deps chromium` (asks for your password) |
| Claude can't find a Jira ticket | Check that you accepted the Jira invite and can open the ticket in your browser. Then check `/mcp` shows Atlassian as connected |
| Search results differ from the lesson | The practice site is shared and its data can change. Tell your teacher which results you see |
