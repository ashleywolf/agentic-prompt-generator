# Agentic Prompt Generator

A pattern library for [GitHub Agentic Workflows](https://github.com/github/gh-aw) — backed by data from **120+ public repos** and **188 compiled workflows** across GitHub.

> **Problem:** Writing a prompt for an agentic workflow that works on the first try is hard. You don't know that a weekly report needs data pre-fetched in a bash step, that a triage workflow should use `gpt-5.1-codex-mini` instead of the default model, or that `create-discussion` with `close-older` is the standard pattern for recurring reports.

This library documents what's actually working in production, organized around the **decisions you make when writing a workflow**.

## Quick Start

1. **Pick your archetype** → [Workflow Archetypes](patterns/workflow-archetypes.md)
2. **Copy a starter template** → [Templates](templates/)
3. **Customize using pattern cards** → [Patterns](patterns/)

## Pattern Cards (9 Decision Areas)

| # | Card | Question It Answers |
|---|------|---------------------|
| 1 | [Data Ingestion](patterns/data-ingestion.md) | "My workflow needs a lot of data. How do I feed it?" |
| 2 | [Model Selection](patterns/model-selection.md) | "Which model should I use?" |
| 3 | [Trigger Selection](patterns/trigger-selection.md) | "When should my workflow run?" |
| 4 | [Output Selection](patterns/output-selection.md) | "Where should results go?" |
| 5 | [State Management](patterns/state-management.md) | "How do I remember things across runs?" |
| 6 | [Prompt Structure](patterns/prompt-structure.md) | "How do I write the actual prompt?" |
| 7 | [Safety Configuration](patterns/safety-configuration.md) | "How do I lock this down?" |
| 8 | [Shared Components](patterns/shared-components.md) | "How do I reuse logic across workflows?" |
| 9 | [Workflow Archetypes](patterns/workflow-archetypes.md) | "What type of workflow am I building?" |

## Starter Templates (8 Archetypes)

| Template | Trigger | Model | Timeout | Use Case |
|----------|---------|-------|---------|----------|
| [Issue Triage](templates/issue-triage.md) | `issues:[opened]` | default | 10min | Classify, label, and comment on new issues |
| [CI Doctor](templates/ci-doctor.md) | `workflow_run` (failure) | claude-sonnet-4.5 | 30min | Investigate CI failures and report root cause |
| [Daily Improver](templates/daily-improver.md) | `schedule: daily` | default | 30min | Incremental code improvements via draft PRs |
| [Weekly Report](templates/weekly-report.md) | `schedule: weekly` | opus (recommended) | 60min | Team/org status reports with pre-fetched data |
| [Slash Command](templates/slash-command.md) | `slash_command` | default | 15min | On-demand `/commands` in issues and PRs |
| [Moderation](templates/moderation.md) | `issues/PR:[opened]` | codex-mini | 5min | Spam detection and content moderation |
| [Content Pipeline](templates/content-pipeline.md) | `workflow_dispatch` | configurable | 45min | Multi-stage content creation with chaining |
| [Enterprise SRE](templates/enterprise-sre.md) | `schedule: weekly` | claude-opus-4.6 | 90min | SLO reports with external service integration |

## Top Rules (from analyzing 79 ospo-aw + 40 public workflows)

1. **If >3 API searches → add a pre-step.** Agents hit the 10KB MCP payload limit. Pre-fetch data deterministically to `/tmp/` and tell the agent "DO NOT query the API — read from /tmp/".

2. **Match model to task.** Classification → `gpt-5.1-codex-mini`. Planning/narrative → `claude-opus-4.6`. Investigation → `claude-sonnet-4.5`. Everything else → default.

3. **Always define safe-outputs.** 6/79 ospo-aw workflows had none — the agent couldn't write results anywhere.

4. **Use `create-discussion` for recurring reports.** With `close-older: true` and `expires: 14`. Issues are for actionable items.

5. **Extract shared formatting into imports.** Top prompts are 10-26KB with repeated rules. Keep workflow-specific prompts focused on the *what*.

6. **Add rate-limit delays.** Include "Add a 1-2 second delay between API calls" when prompts have >3 search patterns.

7. **Use `stop-after: +30d`.** Auto-expires scheduled workflows if they break, preventing silent waste.

## Real-World Examples (Catalog)

| Repo | ⭐ | Workflows | Archetype | Health |
|------|----|-----------|-----------|--------|
| [appwrite/appwrite](catalog/appwrite-appwrite.md) | 44K | issue-triage | Issue Triage (batch) | 🟢 |
| [github/gh-aw](catalog/github-gh-aw.md) | 3.3K | 23 workflows | Mixed | 🟢 |
| [BabylonJS/Babylon.js](catalog/babylonjs-babylon.md) | — | code-simplifier | Daily Improver | 🟢 |
| [JanDeDobbeleer/oh-my-posh](catalog/oh-my-posh.md) | — | workflow-doctor | CI Doctor | 🟡 |
| [Olino3/forge](catalog/olino3-forge.md) | — | 4 workflows | Mixed (best imports) | 🟢 |
| [devantler-tech/ksail](catalog/devantler-tech-ksail.md) | — | 5 workflows | Mixed (multi-phase) | 🟢 |
| [github/copilot-sre](catalog/github-copilot-sre.md) | — | SLO report | Enterprise SRE | 🟢 |
| [github/orca](catalog/github-orca.md) | — | a11y + digest | Daily Improver + Report | 🟢 |
| [github/blog-agent-factory](catalog/github-blog-agent-factory.md) | — | drafter + feedback | Content Pipeline | 🟢 |
| [f/prompts.chat](catalog/f-prompts-chat.md) | — | spam-check | Moderation | 🟢 |

[Full activity report →](data/activity-report.md)

## Self-Updating

This library maintains itself using 3 agentic workflows:

| Workflow | Schedule | What It Does |
|----------|----------|-------------|
| [discover-workflows](.github/workflows/discover-workflows.md) | Weekly (Mon) | Searches GitHub for new repos with `.lock.yml` files |
| [analyze-patterns](.github/workflows/analyze-patterns.md) | Weekly (Wed) | Reads new workflow definitions, extracts patterns, updates library via PR |
| [health-check](.github/workflows/health-check.md) | Monthly (1st) | Verifies existing workflows are still active, removes dead entries |

## Data

- [`data/registry.json`](data/registry.json) — Machine-readable catalog of all 120 repos + 188 workflows
- [`data/activity-report.md`](data/activity-report.md) — Health dashboard for tracked repos

## Discovery Methodology

See [DISCOVERY.md](DISCOVERY.md) for how we found these repos.

## Related

- [github/gh-aw](https://github.com/github/gh-aw) — The agentic workflow compiler and runtime
- [githubnext/agentics](https://github.com/githubnext/agentics) — Official sample pack
- [awesome-agentic-workflows](https://github.com/ashleywolf/awesome-agentic-workflows) — Curated list of workflows and patterns
- [ospo-aw#885](https://github.com/github/ospo-aw/issues/885) — The analysis that inspired this library

## License

MIT
