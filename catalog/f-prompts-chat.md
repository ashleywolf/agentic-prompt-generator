# f/prompts.chat

> **ChatGPT prompts collection** · [f/prompts.chat](https://github.com/f/prompts.chat)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 1 |
| **Last Run** | Event-driven (on issues + PRs) |
| **Primary Model** | gpt-5.1-codex-mini |

---

## Why This Repo Is Notable

This repo handles a classic open-source problem — **spam and low-quality contributions** — with an agentic workflow. The `spam-check` workflow is event-driven, firing on every issue and PR to validate contributions. Since the repo's core content is a CSV file of prompts, the workflow includes **CSV edit validation** to ensure contributions don't corrupt the data format. The multi-signal spam detection approach is a good template for any community-driven repo.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `spam-check` | `issues`, `pull_request` | gpt-5.1-codex-mini | [Triage](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Event-Driven on Issues + PRs
The workflow triggers on both `issues: opened` and `pull_request: opened`, covering all contribution vectors. Uses `gpt-5.1-codex-mini` for fast, low-cost classification.
- **Trigger pattern**: [Event-driven triggers](../patterns/trigger-selection.md)
- **Model pattern**: [Model selection — fast tier](../patterns/model-selection.md)

### CSV Edit Validation
Since the repo's primary content is a CSV file of prompts, the workflow validates that PR changes:
- Don't break CSV structure (missing columns, unescaped commas)
- Don't duplicate existing prompts
- Follow the expected format (title, prompt text, category)
- **Data pattern**: [Data validation](../patterns/data-ingestion.md)

### Multi-Signal Spam Detection
The agent evaluates multiple signals before flagging content as spam:
- Account age and history
- Content quality and relevance
- Pattern matching against known spam templates
- Cross-reference with existing prompts for duplicates
- **Prompt pattern**: [Multi-criteria evaluation](../patterns/prompt-structure.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/f/prompts.chat/tree/main/.github/agents)
- [`spam-check.md`](https://github.com/f/prompts.chat/blob/main/.github/agents/spam-check.md)
