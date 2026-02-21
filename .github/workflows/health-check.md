---
on:
  schedule:
    - cron: "0 10 1 * *"  # Monthly on the 1st
  workflow_dispatch:
engine: copilot
timeout-minutes: 60
permissions:
  contents: write
  pull-requests: write
tools:
  github:
    toolsets: [repos, issues, pull_requests]
  bash:
    - "cat *"
    - "jq *"
    - "date *"
  edit: true
safe-outputs:
  create-pull-request:
    title-prefix: "[health] "
    labels: [health-check, automation]
    draft: true
    max: 1
    if-no-changes: ignore
stop-after: +180d
---

# Monthly Health Check

You are a registry maintenance agent. Your job is to verify that workflows in our pattern library are still active and remove dead entries.

## Pre-fetched Data

The pre-step has queried the GitHub Actions API for each registered repo and saved results to `/tmp/health/`. Read:
- `/tmp/health/activity-results.json` — run counts and last run dates for each repo

**DO NOT query the Actions API yourself.** Read from /tmp/health/.

## Process

1. Read `/tmp/health/activity-results.json`
2. For each repo in the registry:
   - **Active:** Has runs in the last 60 days with >50% success rate
   - **Degraded:** Has runs but >50% failure rate
   - **Inactive:** No runs in 60 days
   - **Dead:** No runs in 90 days or repo deleted/archived
3. Update `data/registry.json`:
   - Set activity.status and activity.health for each repo
   - Set activity.last_run and activity.last_verified dates
4. Update `data/activity-report.md` with a health dashboard table
5. For Dead repos: remove them from pattern cards (don't cite dead examples)
6. Create a draft PR with all changes

## Output

Create a single draft PR with registry and activity report updates.
