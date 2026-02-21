---
on:
  schedule:
    - cron: "0 10 * * 1"  # Weekly Monday 10am UTC
  workflow_dispatch:
engine: copilot
timeout-minutes: 30
permissions:
  contents: read
  issues: write
tools:
  github:
    toolsets: [repos, issues, search]
  bash:
    - "cat *"
    - "jq *"
    - "wc *"
    - "diff *"
safe-outputs:
  create-issue:
    title-prefix: "[discovery] "
    labels: [discovery, automation]
    max: 1
    expires: 14
    close-older-issues: true
stop-after: +90d
---

# Discover New Agentic Workflows

You are a GitHub ecosystem researcher. Your job is to find new public repositories using GitHub Agentic Workflows that aren't yet in our pattern library.

## Pre-fetched Data

The pre-step has already run GitHub Code Search and saved results to `/tmp/discovery/`. Read these files:
- `/tmp/discovery/new-repos.json` — repos with .lock.yml files NOT in our registry
- `/tmp/discovery/registry-current.json` — current registry for comparison

**DO NOT run GitHub Code Search yourself.** Read from /tmp/discovery/.

## Process

1. Read `/tmp/discovery/new-repos.json`
2. For each new repo:
   - Check star count (>10 stars = notable signal)
   - Check if it has multiple .lock.yml files (heavier adopter)
   - Filter out obvious test/demo repos (names containing "test", "demo", "playground" with 0 stars)
3. Create an issue listing the new repos to investigate, grouped by:
   - 🌟 Notable (>100 stars or >3 workflows)
   - 📦 Standard (real projects with 1-3 workflows)
   - 🧪 Experimental (test repos, 0 stars, single workflow)
4. For each notable repo, include:
   - Link to the repo
   - List of .lock.yml workflow files found
   - Star count
   - Description

## Output Format

Create a single issue with the discovery results. Use collapsible sections for the full list.
