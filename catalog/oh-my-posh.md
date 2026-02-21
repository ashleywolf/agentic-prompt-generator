# JanDeDobbeleer/oh-my-posh

> **Terminal prompt theme engine** · [JanDeDobbeleer/oh-my-posh](https://github.com/JanDeDobbeleer/oh-my-posh)

| Field | Value |
|-------|-------|
| **Status** | 🟡 Degraded — workflow may have stalled |
| **Workflows** | 1 |
| **Last Run** | CI-failure triggered |
| **Primary Model** | claude-sonnet-4.5 |

---

## Why This Repo Is Notable

oh-my-posh's `workflow-doctor` is a **CI failure investigation agent** — it activates when GitHub Actions workflows fail and attempts to diagnose the root cause. Notable for using `claude-sonnet-4.5` (higher reasoning for complex debugging), a **6-phase investigation protocol**, and a **file-based knowledge base** in `/tmp/memory/` for cross-run learning. Uses `stop-after: +1mo` for auto-expiration. Marked 🟡 due to potential staleness.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `workflow-doctor` | `workflow_run: completed` (failure) | claude-sonnet-4.5 | [Investigator](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### 6-Phase Investigation Protocol
The workflow follows a structured diagnostic sequence:
1. **Collect** — gather failed workflow run logs and context
2. **Identify** — isolate the failing step and error message
3. **Correlate** — check if this failure has occurred before (via memory)
4. **Diagnose** — determine root cause (flaky test, dependency issue, config drift)
5. **Recommend** — suggest a fix with specific code/config changes
6. **Report** — post a diagnostic comment on the commit or PR

- **Prompt pattern**: [Numbered steps](../patterns/prompt-structure.md)

### File-Based Knowledge Base (`/tmp/memory/`)
Instead of using cache-memory or discussions, the agent writes diagnostic findings to files in `/tmp/memory/`, building a local knowledge base of past failures. This enables cross-run correlation without platform-level state.
- **State pattern**: [File-based memory](../patterns/state-management.md)

### `claude-sonnet-4.5` for Investigation
Uses a higher-tier model (`claude-sonnet-4.5`) because CI failure diagnosis requires:
- Reading and understanding complex log output
- Correlating multiple failure signals
- Reasoning about build system behavior
- **Model pattern**: [Model selection — reasoning tier](../patterns/model-selection.md)

### `stop-after: +1mo` (Auto-Expiration)
Auto-disables after one month to prevent the investigation agent from running indefinitely on a repo that may have moved to a different CI strategy.
- **Safety pattern**: [Safety Configuration](../patterns/safety-configuration.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/JanDeDobbeleer/oh-my-posh/tree/main/.github/agents)
- [`workflow-doctor.md`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/agents/workflow-doctor.md)
