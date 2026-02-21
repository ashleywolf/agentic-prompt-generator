# BabylonJS/Babylon.js

> **3D game engine for the web** · [BabylonJS/Babylon.js](https://github.com/BabylonJS/Babylon.js)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 1 |
| **Last Run** | Daily |
| **Primary Model** | claude-sonnet-4 |

---

## Why This Repo Is Notable

Babylon.js uses a **4-phase code simplification workflow** that demonstrates disciplined, incremental refactoring at scale. The workflow finds recent changes, analyzes them against coding standards, simplifies one thing per run, then validates the change compiles. The **one-change-per-run** constraint and **skip-if-existing-PR** guard make this a model for safe autonomous refactoring in large codebases.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `code-simplifier` | `schedule: daily` | claude-sonnet-4 | [Code Improver](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### 4-Phase Pipeline
The workflow executes a strict sequence:
1. **Find changes** — identify files changed in the last 7 days
2. **Analyze standards** — compare against the project's coding conventions
3. **Simplify** — make exactly one simplification (rename, extract, inline)
4. **Validate** — ensure the change compiles and tests pass

This phased approach prevents the agent from making sweeping changes that break things.
- **Prompt pattern**: [Numbered steps](../patterns/prompt-structure.md)

### Skip If Existing PR
Before starting, the workflow checks if it already has an open PR. If so, it exits immediately — preventing pile-up of competing refactoring PRs.
- **Safety pattern**: [Safety Configuration](../patterns/safety-configuration.md)

### One-Change-Per-Run
The prompt explicitly constrains the agent to make **exactly one simplification per run**. This keeps PRs small, reviewable, and easy to revert.
- **Safety pattern**: [Safety Configuration](../patterns/safety-configuration.md)
- **Prompt pattern**: [Guardrails in prompts](../patterns/prompt-structure.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/BabylonJS/Babylon.js/tree/main/.github/agents)
- [`code-simplifier.md`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/agents/code-simplifier.md)
