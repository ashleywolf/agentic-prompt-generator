# appwrite/appwrite

> **Open-source backend platform** · [appwrite/appwrite](https://github.com/appwrite/appwrite) · ⭐ 44,000+

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 1 |
| **Last Run** | Daily batch |
| **Primary Model** | claude-sonnet-4 |

---

## Why This Repo Is Notable

Appwrite demonstrates the **batch triage pattern at scale** — instead of triaging only new issues, the workflow processes **all issues updated in the last 24 hours**, catching state changes that event-driven triggers would miss. It also uses `stop-after: +30d` for automatic expiration, org-wide duplicate search across all appwrite repos, and references `githubnext/agentics` as its source template.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `issue-triage` | `schedule: daily` | claude-sonnet-4 | [Triage](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Batch Triage (All Updated Issues, Not Just New)
Unlike typical triage that runs on `issues: opened`, this workflow runs on a daily schedule and processes every issue updated in the last 24 hours. This catches:
- Issues that changed labels
- Issues that received new comments with reproduction info
- Issues reopened after being closed
- **Trigger pattern**: [Schedule-based batch](../patterns/trigger-selection.md)

### `stop-after: +30d` (Auto-Expiration)
The workflow is configured to automatically stop running after 30 days, requiring explicit re-enablement. This prevents forgotten workflows from consuming resources indefinitely.
- **Safety pattern**: [Safety Configuration](../patterns/safety-configuration.md)

### Org-Wide Duplicate Search
Before labeling a new issue, the agent searches across **all appwrite/* repositories** for duplicates — not just the current repo. This catches cross-repo duplicates in the appwrite ecosystem.

### Source Reference
Uses `source:` front matter referencing [`githubnext/agentics`](https://github.com/githubnext/agentics) as its template origin.

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/appwrite/appwrite/tree/main/.github/agents)
- [`issue-triage.md`](https://github.com/appwrite/appwrite/blob/main/.github/agents/issue-triage.md)
