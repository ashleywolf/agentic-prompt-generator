---
name: scan-agentic-workflows
description: Weekly scan for new agentic workflow repos and patterns, auto-updating data
on:
  schedule:
    - cron: "0 8 * * 1"
  workflow_dispatch:
stop-after: +30d
tools:
  - create-pull-request
pre-steps:
  - name: Run scan pipeline
    run: |
      chmod +x scripts/scan.sh
      ./scripts/scan.sh --active-only --run-history --with-logs
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
---

# Agentic Workflow Scanner

You are a research agent that analyzes the latest scan of GitHub Agentic Workflows.

## Instructions

1. Read the freshly generated `data/scan-results.json` from the pre-step.
2. Compare with the current repository data to identify:
   - **New repos** — Repositories not previously tracked
   - **New workflow patterns** — Novel trigger/tool/model combinations
   - **Trending repos** — Repos with significant star or activity growth
   - **Inactive repos** — Previously active repos that are now dormant
3. For each new pattern discovered, determine if it fits an existing category in `patterns/` or represents a new category.
4. Prepare updates:
   - Update `data/scan-results.json` with the new scan data (already done by pre-step)
   - Suggest new or updated entries for pattern catalog files in `catalog/`
   - Note any repos that would make good new template sources
5. Create a pull request with:
   - Title: `data: weekly scan update — [date]`
   - Branch: `scan/weekly-[date]`
   - Body containing:
     - Summary of new repos found
     - New patterns identified
     - Repos that became inactive
     - Suggested template additions

## Guidelines

- Only reference public repositories visible in scan-results.json
- Do not fabricate repository names or URLs
- Keep the PR description concise — link to details in changed files
- If no meaningful changes are found, create a minimal PR noting "no significant changes"
