# Olino3/forge

> **Claude Code plugin marketplace** · [Olino3/forge](https://github.com/Olino3/forge)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 4 workflows sharing 5 base modules |
| **Last Run** | Daily / event-driven |
| **Primary Models** | gpt-5.1-codex-mini (detection), claude-opus-4.6 (planning) |

---

## Why This Repo Is Notable

Forge has the **best import architecture outside github/gh-aw** — 4 workflows share 5 base modules, demonstrating clean separation of concerns. It also shows effective **model tiering**: cheap `gpt-5.1-codex-mini` for fast detection/classification, expensive `claude-opus-4.6` for complex planning. The `forge-milestone-lifecycle` workflow is a standout example of the multi-trigger routing pattern.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `forge-milestone-lifecycle` | `issues`, `milestone`, `schedule` | claude-opus-4.6 | [Campaign](../patterns/workflow-archetypes.md) |
| 2 | `forge-plugin-review` | `pull_request` | gpt-5.1-codex-mini | [Code Reviewer](../patterns/workflow-archetypes.md) |
| 3 | `forge-catalog-sync` | `schedule: daily` | gpt-5.1-codex-mini | [Recurring Auditor](../patterns/workflow-archetypes.md) |
| 4 | `forge-release-notes` | `release` | claude-opus-4.6 | [Reporter](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Multi-Trigger Routing (`forge-milestone-lifecycle`)
A single workflow handles three different triggers (`issues`, `milestone`, `schedule`) by routing to different prompt sections based on the event type. This avoids duplicating shared logic across multiple workflow files.
- **Trigger pattern**: [Multi-trigger routing](../patterns/trigger-selection.md)

### Model Tiering Strategy
Deliberate separation of models by task complexity:
- **Detection/classification**: `gpt-5.1-codex-mini` — fast, cheap, good enough for binary decisions
- **Planning/generation**: `claude-opus-4.6` — expensive but needed for nuanced multi-step reasoning
- **Model pattern**: [Model selection](../patterns/model-selection.md)

### Import Architecture (5 Base Modules)
All 4 workflows share these reusable modules:
```
.github/agents/
├── modules/
│   ├── plugin-schema.md       # Plugin manifest validation
│   ├── marketplace-rules.md   # Submission/quality rules
│   ├── review-checklist.md    # Shared review criteria
│   ├── release-format.md      # Release note templates
│   └── catalog-format.md      # Catalog entry schema
├── forge-milestone-lifecycle.md
├── forge-plugin-review.md
├── forge-catalog-sync.md
└── forge-release-notes.md
```
- **Pattern**: [Shared Components](../patterns/shared-components.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/Olino3/forge/tree/main/.github/agents)
- [`forge-milestone-lifecycle.md`](https://github.com/Olino3/forge/blob/main/.github/agents/forge-milestone-lifecycle.md)
- [`forge-plugin-review.md`](https://github.com/Olino3/forge/blob/main/.github/agents/forge-plugin-review.md)
- [`forge-catalog-sync.md`](https://github.com/Olino3/forge/blob/main/.github/agents/forge-catalog-sync.md)
- [`forge-release-notes.md`](https://github.com/Olino3/forge/blob/main/.github/agents/forge-release-notes.md)
