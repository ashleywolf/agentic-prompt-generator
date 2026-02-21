# github/blog-agent-factory

> **Content pipeline for the GitHub Blog** · [github/blog-agent-factory](https://github.com/github/blog-agent-factory)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 2 |
| **Last Run** | Daily / slash command |
| **Primary Model** | claude-sonnet-4, claude-opus-4.6 |

---

## Why This Repo Is Notable

blog-agent-factory is the best example of a **multi-workflow pipeline** — three agents (scout, drafter, linker) chain together via `dispatch-workflow` to move blog posts from idea to draft to published. The `feedback` workflow uses a slash command for on-demand editorial review. It also demonstrates **tone calibration** (matching the GitHub blog's voice), an **extensive style guide** imported as a shared component, and `hide-older-comments` to keep PR threads clean.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `blog-drafter` | `schedule: daily` + `workflow_dispatch` | claude-opus-4.6 | [Content Generator](../patterns/workflow-archetypes.md) |
| 2 | `feedback` | Slash command (`/feedback`) | claude-sonnet-4 | [Code Reviewer](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Multi-Workflow Pipeline (Scout → Drafter → Linker)
Three agents chain together using `dispatch-workflow`:
1. **Scout** — finds topics worth writing about (new features, trends, community stories)
2. **Drafter** — writes the initial blog post draft from the scout's brief
3. **Linker** — adds internal links, CTAs, and SEO metadata

Each stage triggers the next via `workflow_dispatch`, passing context through workflow inputs.
- **Trigger pattern**: [Workflow chaining via dispatch](../patterns/trigger-selection.md)
- **Archetype**: [Content Generator](../patterns/workflow-archetypes.md)

### Tone Calibration
The prompt includes detailed tone guidance to match the GitHub blog's established voice:
- Conversational but authoritative
- Developer-first (show code, not marketing speak)
- Specific over general (name the feature, show the command)
- **Prompt pattern**: [Role + voice calibration](../patterns/prompt-structure.md)

### Extensive Style Guide (Shared Component)
An imported style guide module defines:
- Heading conventions
- Code block formatting
- Image/screenshot requirements
- Link text patterns
- Blog-specific terminology
- **Import pattern**: [Shared Components](../patterns/shared-components.md)

### `hide-older-comments`
When the `feedback` workflow posts a new review comment, it hides (minimizes) older bot comments on the same PR to prevent thread clutter.
- **Output pattern**: [Comment management](../patterns/output-selection.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/github/blog-agent-factory/tree/main/.github/agents)
- [`blog-drafter.md`](https://github.com/github/blog-agent-factory/blob/main/.github/agents/blog-drafter.md)
- [`feedback.md`](https://github.com/github/blog-agent-factory/blob/main/.github/agents/feedback.md)
