# github/gh-aw

> **Official GitHub Agentic Workflows tooling repo** · [github/gh-aw](https://github.com/github/gh-aw) · ⭐ 3,352

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 23 total, 14 actively running |
| **Last Run** | Daily (multiple schedules) |
| **Primary Models** | gpt-5.1-codex-mini, claude-sonnet-4, claude-opus-4.6 |

---

## Why This Repo Is Notable

This is the **reference implementation** for GitHub's agentic workflows platform. It has the largest collection of production workflows, the best import architecture (`shared/` directory with reusable modules), and demonstrates nearly every pattern documented in this catalog. If you're building your first workflow, start by reading the prompts here.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `pr-nitpick-reviewer` | Slash command | gpt-5.1-codex-mini | [Code Reviewer](../patterns/workflow-archetypes.md) |
| 2 | `delight` | `schedule: daily` | claude-sonnet-4 | [Recurring Auditor](../patterns/workflow-archetypes.md) |
| 3 | `security-compliance` | `schedule: daily` | claude-opus-4.6 | [Campaign](../patterns/workflow-archetypes.md) |
| 4 | `portfolio-analyst` | `schedule: weekly` | claude-opus-4.6 | [Reporter](../patterns/workflow-archetypes.md) |
| 5 | `ai-moderator` | `issues`, `issue_comment` | gpt-5.1-codex-mini | [Triage](../patterns/workflow-archetypes.md) |
| 6–23 | *(14 more actively running, 9 archived)* | Various | Various | Various |

---

## Key Patterns

### Slash Command + Cache-Memory (`pr-nitpick-reviewer`)
Combines event-driven slash command triggering with persistent cache-memory to track reviewer preferences over time.
- **Trigger pattern**: [Slash commands](../patterns/trigger-selection.md)
- **State pattern**: [Cache-memory](../patterns/state-management.md)

### Daily UX Audit + Repo-Memory (`delight`)
Runs daily to surface UX friction in the product, storing findings in repo-memory to avoid duplicate reports.
- **State pattern**: [Repo-memory via files](../patterns/state-management.md)
- **Output pattern**: [Discussion-based reporting](../patterns/output-selection.md)

### Campaign Pattern (`security-compliance`)
Multi-day campaign that tracks compliance status across the codebase, creating issues for each finding and closing them when resolved.
- **Archetype**: [Campaign](../patterns/workflow-archetypes.md)
- **State pattern**: [Issue-as-state](../patterns/state-management.md)

### Pre-Step Data + Charts (`portfolio-analyst`)
Uses a pre-step to fetch API data before the agent runs, then generates charts for the weekly report.
- **Data pattern**: [Pre-step data ingestion](../patterns/data-ingestion.md)
- **Output pattern**: [Discussion with artifacts](../patterns/output-selection.md)

### Lightweight Fast Model (`ai-moderator`)
Uses `gpt-5.1-codex-mini` for fast, low-cost moderation decisions on every issue and comment.
- **Model pattern**: [Model selection — fast tier](../patterns/model-selection.md)

---

## Import Architecture (Best-in-Class)

The `shared/` directory is the gold standard for reusable prompt components:

```
.github/agents/
├── shared/
│   ├── reporting.md          # Shared output formatting templates
│   ├── jqschema.md           # JSON schema validation helpers
│   └── mcp/
│       ├── github.md         # GitHub MCP server usage guide
│       ├── fetch.md          # HTTP fetch patterns
│       └── memory.md         # Cache-memory usage patterns
├── pr-nitpick-reviewer.md
├── delight.md
├── security-compliance.md
└── ...
```

Workflows import shared modules using `imports:` in their front matter, keeping prompts DRY and consistent.
- **Pattern**: [Shared Components](../patterns/shared-components.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/github/gh-aw/tree/main/.github/agents)
- [`shared/reporting.md`](https://github.com/github/gh-aw/blob/main/.github/agents/shared/reporting.md)
- [`shared/jqschema.md`](https://github.com/github/gh-aw/blob/main/.github/agents/shared/jqschema.md)
- [`shared/mcp/`](https://github.com/github/gh-aw/tree/main/.github/agents/shared/mcp)
