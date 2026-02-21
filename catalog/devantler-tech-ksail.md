# devantler-tech/ksail

> **Kubernetes cluster management toolkit** · [devantler-tech/ksail](https://github.com/devantler-tech/ksail)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 5 |
| **Last Run** | Daily (multiple schedules) |
| **Primary Models** | claude-sonnet-4, gpt-5.1-codex |

---

## Why This Repo Is Notable

ksail demonstrates **multi-phase workflows with discussion-as-state** — a pattern where GitHub Discussions serve as persistent state stores across runs. It also uses Playwright for visual regression testing (screenshots in PRs), cache-memory for tracking doc freshness, and slash commands for on-demand operations. Strong example of a mid-size repo fully embracing agentic workflows.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `plan` | Slash command | claude-sonnet-4 | [Planner](../patterns/workflow-archetypes.md) |
| 2 | `daily-backlog-burner` | `schedule: daily` | gpt-5.1-codex | [Campaign](../patterns/workflow-archetypes.md) |
| 3 | `unbloat-docs` | `schedule: daily` | claude-sonnet-4 | [Recurring Auditor](../patterns/workflow-archetypes.md) |
| 4 | `weekly-promote-ksail` | `schedule: weekly` | gpt-5.1-codex | [Reporter](../patterns/workflow-archetypes.md) |
| 5 | `daily-refactor` | `schedule: daily` | claude-sonnet-4 | [Code Improver](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Multi-Phase with Discussion-as-State
Workflows like `daily-backlog-burner` use GitHub Discussions as a persistent scratchpad — writing phase results to a pinned discussion, then reading them back on subsequent runs.
- **State pattern**: [Discussion-as-state](../patterns/state-management.md)
- **Output pattern**: [Discussion-based reporting](../patterns/output-selection.md)

### Cache-Memory for Doc Tracking (`unbloat-docs`)
Tracks which documentation pages were last reviewed and their freshness score using cache-memory with keyed entries.
- **State pattern**: [Cache-memory](../patterns/state-management.md)

### Playwright Screenshots
Visual regression testing — workflows take Playwright screenshots of rendered docs/UI and attach them to PRs for human review.
- **Data pattern**: [Pre-step data ingestion](../patterns/data-ingestion.md)

### Slash Commands (`plan`)
On-demand planning workflow triggered via `/plan` comment on issues, generating a structured implementation plan.
- **Trigger pattern**: [Slash commands](../patterns/trigger-selection.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/devantler-tech/ksail/tree/main/.github/agents)
- [`plan.md`](https://github.com/devantler-tech/ksail/blob/main/.github/agents/plan.md)
- [`daily-backlog-burner.md`](https://github.com/devantler-tech/ksail/blob/main/.github/agents/daily-backlog-burner.md)
- [`unbloat-docs.md`](https://github.com/devantler-tech/ksail/blob/main/.github/agents/unbloat-docs.md)
- [`weekly-promote-ksail.md`](https://github.com/devantler-tech/ksail/blob/main/.github/agents/weekly-promote-ksail.md)
- [`daily-refactor.md`](https://github.com/devantler-tech/ksail/blob/main/.github/agents/daily-refactor.md)
