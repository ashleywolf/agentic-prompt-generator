# Prompt Structure

> **"How do I write the prompt?"**

## The Numbers

From **661 source-available workflows** across **269 repos**, prompt structure varies significantly. The workflow `.md` file itself **is** the prompt — its structure determines how the agent behaves.

| Style | Description | Best For |
|-------|-------------|----------|
| Role + Steps | "You are X. Do 1, 2, 3." | Most workflows |
| Phase-based | Distinct phases with gates | Complex multi-step work |
| Template-driven | Fill-in-the-blank output | Consistent formatting |
| Personality-driven | Character + tone | Community-facing bots |
| Minimal | One-sentence instruction | Simple tasks |

## Decision Table

| Your workflow is… | Style | Why |
|-------------------|-------|-----|
| Issue triage | **Role + Steps** | Clear instructions, consistent output |
| Daily code improvement | **Phase-based** | Analyze → Plan → Implement → Validate |
| Report generation | **Template-driven** | Consistent format across runs |
| Slash command / community bot | **Personality-driven** | Engagement, tone |
| Simple check (links, typos) | **Minimal** | No ambiguity needed |

## Style 1: Role + Steps (Most Common)

Define the agent's role, then list numbered steps. The dominant pattern.

**Real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — "You are a triage agent. 1. Read the issue. 2. Classify. 3. Label." (54,898 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) — Role-based triage instructions (29,779 ⭐)
- [`github/copilot-sdk/issue-triage`](https://github.com/github/copilot-sdk/blob/main/.github/workflows/issue-triage.md) — Structured role + steps (7,254 ⭐)

**Structure:**
```markdown
# Workflow Name

You are a [role] for [repo/project].

## Steps

1. [First action]
2. [Second action]
3. [Output action]

## Rules

- [Constraint 1]
- [Constraint 2]
```

## Style 2: Phase-Based (Complex Work)

Breaks the task into distinct phases with clear transitions. Used when the agent must analyze before acting.

**Real examples:**
- [`BabylonJS/Babylon.js/code-simplifier`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/workflows/code-simplifier.md) — Analyze → Identify → Simplify → Submit (25,113 ⭐)
- [`ohcnetwork/care_fe/daily-playwright-improver`](https://github.com/ohcnetwork/care_fe/blob/main/.github/workflows/daily-playwright-improver.md) — Run tests → Analyze failures → Fix → Validate (606 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Discover → Improve → Test → Submit (509 ⭐)

**Structure:**
```markdown
# Workflow Name

## Phase 1: Analysis
[Read the codebase, identify targets]

## Phase 2: Planning
[Decide what to change and why]

## Phase 3: Implementation
[Make the changes]

## Phase 4: Validation
[Verify changes don't break anything]
```

## Style 3: Template-Driven (Consistent Output)

Provides a template the agent must fill in. Ensures consistent formatting.

**Real examples:**
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) — Status report template (23,180 ⭐)
- [`erigontech/erigon/daily-repo-status`](https://github.com/erigontech/erigon/blob/main/.github/workflows/daily-repo-status.md) — Templated daily status (3,531 ⭐)
- [`stride3d/stride-community-toolkit/daily-activity-report`](https://github.com/stride3d/stride-community-toolkit/blob/main/.github/workflows/daily-activity-report.md) — Activity report template (112 ⭐)

**Structure:**
```markdown
# Daily Status Report

Generate a status report using this template:

## Summary
[One-line summary of repo health]

## Open Issues
| Priority | Count | Change |
|----------|-------|--------|
| Critical | [N]   | [+/-]  |
| High     | [N]   | [+/-]  |

## Action Items
- [Item 1]
- [Item 2]
```

## Style 4: Personality-Driven (Community Bots)

Defines a character with a specific tone. Used for community-facing interactions.

**Real examples:**
- [`github/gh-aw/poem-bot`](https://github.com/github/gh-aw/blob/main/.github/workflows/poem-bot.md) — Responds with poetry, uses `gpt-5` model (3,356 ⭐)
- [`github/gh-aw/grumpy-reviewer`](https://github.com/github/gh-aw/blob/main/.github/workflows/grumpy-reviewer.md) — Deliberately grumpy code reviews via slash command (3,356 ⭐)
- [`github/gh-aw/delight`](https://github.com/github/gh-aw/blob/main/.github/workflows/delight.md) — Delightful community engagement (3,356 ⭐)
- [`ohcnetwork/care_fe/thank-you-note`](https://github.com/ohcnetwork/care_fe/blob/main/.github/workflows/thank-you-note.md) — Thank contributors with personality (606 ⭐)

## Style 5: Minimal (Simple Tasks)

A short, direct instruction. No role, no phases, just the task.

**Real examples:**
- [`llm-d/llm-d/typo-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/typo-checker.md) — Check for typos in the PR (2,516 ⭐)
- [`llm-d/llm-d/link-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/link-checker.md) — Verify links in the PR (2,516 ⭐)
- [`plengauer/Thoth/autoapprove`](https://github.com/plengauer/Thoth/blob/main/.github/workflows/autoapprove.md) — Simple auto-approve logic (150 ⭐)

## Prompt Engineering Patterns from the Scan

### The "Rules" Section

Many high-star workflows include explicit rules/constraints:
- [`evcc-io/evcc/triage-agent`](https://github.com/evcc-io/evcc/blob/main/.github/workflows/triage-agent.md) — Rules about when NOT to label (6,169 ⭐)
- [`f/prompts.chat/spam-check`](https://github.com/f/prompts.chat/blob/main/.github/workflows/spam-check.md) — Spam detection criteria (145,906 ⭐)

### The "Context" Section

Workflows that need repo-specific knowledge embed it in the prompt:
- [`phpstan/phpstan/generate-error-docs`](https://github.com/phpstan/phpstan/blob/main/.github/workflows/generate-error-docs.md) — PHPStan-specific error types (13,829 ⭐)
- [`npgsql/efcore.pg/sync-to-latest-ef`](https://github.com/npgsql/efcore.pg/blob/main/.github/workflows/sync-to-latest-ef.md) — EF Core sync context (1,801 ⭐)

## Rules

1. **Start with Role + Steps.** It's the most common pattern and works for 80% of workflows.
2. **Use phases for code-change workflows.** Analyze → Plan → Implement → Validate prevents the agent from jumping to code changes prematurely.
3. **Use templates when output format matters.** Daily reports, status updates, and anything humans will scan quickly.
4. **Personality is optional.** Only use it for community-facing bots where tone matters.
5. **Include a "Rules" section** to define what the agent should NOT do. Constraints are as important as instructions.
6. **Embed domain context** directly in the prompt when the agent needs project-specific knowledge.
7. **Keep it minimal for simple tasks.** A typo checker doesn't need a role definition.
