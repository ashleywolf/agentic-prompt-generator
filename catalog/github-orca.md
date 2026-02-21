# github/orca

> **GitHub product repository** · [github/orca](https://github.com/github/orca)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 2 |
| **Last Run** | Daily / twice-weekly |
| **Primary Model** | claude-sonnet-4 |

---

## Why This Repo Is Notable

github/orca uses agentic workflows for **accessibility compliance** and **ship visibility**. The `daily-accessibility-review` workflow scans for WCAG 2.2 violations — a novel use case for agentic workflows that goes beyond typical code review. The `daily-ship-digest` compiles shipping activity into a twice-weekly summary. Both workflows reference `githubnext/agentics` as their source template.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `daily-accessibility-review` | `schedule: daily` | claude-sonnet-4 | [Recurring Auditor](../patterns/workflow-archetypes.md) |
| 2 | `daily-ship-digest` | `schedule: twice-weekly` | claude-sonnet-4 | [Reporter](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### WCAG 2.2 Compliance Scanning (`daily-accessibility-review`)
The agent reviews recent UI changes against WCAG 2.2 accessibility guidelines, checking for:
- Missing alt text on images
- Insufficient color contrast
- Missing ARIA labels
- Keyboard navigation gaps
- Focus management issues

This is a high-value use case — accessibility violations are easy to introduce and hard to catch in manual review.
- **Archetype**: [Recurring Auditor](../patterns/workflow-archetypes.md)
- **Prompt pattern**: [Checklist-based evaluation](../patterns/prompt-structure.md)

### Twice-Weekly Ship Digest (`daily-ship-digest`)
Compiles merged PRs, deployed changes, and notable commits into a team-readable digest. Runs twice per week (not daily, despite the name) to balance signal-to-noise.
- **Output pattern**: [Discussion-based reporting](../patterns/output-selection.md)
- **Trigger pattern**: [Schedule-based](../patterns/trigger-selection.md)

### Source Reference
Both workflows use `source:` front matter referencing [`githubnext/agentics`](https://github.com/githubnext/agentics) as their template origin, indicating they were bootstrapped from the official template library.

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/github/orca/tree/main/.github/agents)
- [`daily-accessibility-review.md`](https://github.com/github/orca/blob/main/.github/agents/daily-accessibility-review.md)
- [`daily-ship-digest.md`](https://github.com/github/orca/blob/main/.github/agents/daily-ship-digest.md)
