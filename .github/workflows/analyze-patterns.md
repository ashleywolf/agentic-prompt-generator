---
on:
  schedule:
    - cron: "0 10 * * 3"  # Weekly Wednesday 10am UTC
  workflow_dispatch:
engine: copilot
timeout-minutes: 45
permissions:
  contents: write
  issues: read
  pull-requests: write
tools:
  github:
    toolsets: [repos, issues, pull_requests, search]
  bash:
    - "cat *"
    - "jq *"
  edit: true
safe-outputs:
  create-pull-request:
    title-prefix: "[patterns] "
    labels: [patterns, automation]
    draft: true
    max: 1
    if-no-changes: ignore
  create-issue:
    title-prefix: "[new-pattern] "
    labels: [new-pattern]
    max: 2
stop-after: +90d
imports:
  - shared/reporting.md
---

# Analyze New Workflow Patterns

You are an agentic workflow pattern analyst. Your job is to read workflow definitions from newly discovered repos and extract patterns to update the pattern library.

## Process

1. **Find repos to analyze:** Search for open issues with the `discovery` label (created by the discover-workflows agent)
2. **For each repo in the discovery issue:**
   - Use the GitHub API to read each `.md` workflow file from `.github/workflows/`
   - Extract: trigger type, engine, model, tools/toolsets, safe-outputs, imports, pre-steps
   - Classify into existing archetype: issue-triage, ci-doctor, daily-improver, weekly-report, slash-command, moderation, content-pipeline, enterprise-sre
   - Note any patterns NOT in our existing library
3. **Update registry:** Edit `data/registry.json` to add the new repo and workflow entries with full metadata
4. **Update pattern cards:** If a workflow demonstrates a pattern better than existing examples, or uses a novel approach, edit the relevant pattern card in `patterns/` to add it
5. **Flag new patterns:** If you find a genuinely new pattern not covered by existing cards, create an issue proposing a new pattern card

## Classification Rules

- Trigger `issues:[opened]` + labels output → **issue-triage**
- Trigger `workflow_run` + failure analysis → **ci-doctor**
- Trigger `schedule:daily` + PR output → **daily-improver**
- Trigger `schedule:weekly` + discussion/issue output → **weekly-report**
- Trigger `slash_command` → **slash-command**
- Trigger `issues/PR` + spam/label detection → **moderation**
- Trigger `workflow_dispatch` + `dispatch-workflow` output → **content-pipeline**
- Complex multi-service + keyed cache + artifacts → **enterprise-sre**

## Output

Create a draft PR updating `data/registry.json` and any pattern card files that were improved.
If new patterns are found, create issues describing them.
