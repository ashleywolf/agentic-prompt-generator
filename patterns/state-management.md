# State Management

> **"How do I remember across runs?"**

## The Numbers

From **679 workflows** across **269 repos**, the vast majority are **stateless** — each run is independent. State management is an advanced pattern used by workflows that need to track progress, remember decisions, or accumulate knowledge.

| Pattern | Complexity | Durability | Use Case |
|---------|-----------|------------|----------|
| Stateless | None | N/A | Most workflows (triage, review) |
| Issue-as-state | Low | Persistent | Track recurring work |
| Discussion-as-state | Low | Persistent | Reports, threaded analysis |
| Repo-memory (files) | Medium | Persistent | Config, learned rules |
| Cache-memory | Medium | Ephemeral | Between workflow steps |
| Branch-as-workspace | Medium | Persistent | Multi-run improvements |

## Decision Table

| You need to… | Pattern | Why |
|--------------|---------|-----|
| Just respond to an event | **Stateless** | No memory needed |
| Track what you triaged today | **Issue-as-state** | The issue itself is the record |
| Accumulate daily findings | **Discussion-as-state** | Threaded, searchable |
| Remember rules learned over time | **Repo-memory** | Committed to repo |
| Continue multi-day improvements | **Branch-as-workspace** | PR stays open across runs |
| Pass data between pre-step and agent | **Cache-memory** | Workflow-scoped |

## Pattern 1: Stateless (Majority of Workflows)

Each run is independent. The agent reads the current event, responds, and forgets.

**Real examples:**
- [`f/prompts.chat/spam-check`](https://github.com/f/prompts.chat/blob/main/.github/workflows/spam-check.md) — Each PR checked independently (145,906 ⭐)
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — Each issue triaged independently (54,898 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) — No cross-issue memory (29,779 ⭐)

**When to use:** The event contains everything the agent needs. This is the default — don't add state unless you need it.

## Pattern 2: Issue-as-State (Tracking Issues)

Use a GitHub Issue as a persistent tracking mechanism. The issue body or comments store state.

**Real examples:**
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) — Creates daily status issues, each a snapshot (23,180 ⭐)
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) — Daily issues as historical record (5,457 ⭐)
- [`stride3d/stride-community-toolkit/daily-activity-report`](https://github.com/stride3d/stride-community-toolkit/blob/main/.github/workflows/daily-activity-report.md) — Activity tracked via issues (112 ⭐)

**How it works:** Each daily run creates an issue. Previous issues form a queryable history. The agent can read past issues to spot trends.

## Pattern 3: Discussion-as-State

GitHub Discussions provide threaded, persistent storage for reports and analysis.

**Real examples:**
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) — Posts status to Discussions alongside issues, threads accumulate over time (5,457 ⭐)
- [`lablup/backend.ai-webui/weekly-team-status`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/weekly-team-status.md) — Team status tracked in Discussions with 6-month window (125 ⭐)
- [`devantler-tech/ksail/plan`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/plan.md) — Planning discussions threaded for follow-up (130 ⭐)

**When to use:** Long-form reports, community-facing summaries, or anything benefiting from threaded follow-up.

## Pattern 4: Repo-Memory (Committed Files)

Store state in the repository itself — config files, learned rules, or accumulated data.

**Real examples:**
- [`phpstan/phpstan/generate-error-docs`](https://github.com/phpstan/phpstan/blob/main/.github/workflows/generate-error-docs.md) — Generated docs committed to repo (13,829 ⭐)
- [`npgsql/efcore.pg/sync-to-latest-ef`](https://github.com/npgsql/efcore.pg/blob/main/.github/workflows/sync-to-latest-ef.md) — Sync changes committed via PR (1,801 ⭐)
- [`phpstan/phpstan-src/document-config-params`](https://github.com/phpstan/phpstan-src/blob/main/.github/workflows/document-config-params.md) — Config documentation committed on push (385 ⭐)

**How it works:** The agent makes changes and commits them (via PR). The repo itself becomes the memory.

## Pattern 5: Branch-as-Workspace

Use a long-lived branch as a workspace for multi-run improvements. Each run adds commits to the same branch/PR.

**Real examples:**
- [`BabylonJS/Babylon.js/code-simplifier`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/workflows/code-simplifier.md) — Scheduled simplification, accumulates in PRs (25,113 ⭐)
- [`ohcnetwork/care_fe/daily-playwright-improver`](https://github.com/ohcnetwork/care_fe/blob/main/.github/workflows/daily-playwright-improver.md) — Daily test improvements on a branch (606 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Iterative test improvement (509 ⭐)
- [`devantler-tech/ksail/daily-perf-improver`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/daily-perf-improver.md) — Performance work across days (130 ⭐)

**How it works:** Each scheduled run picks up where the last left off. The branch accumulates changes. A human reviews and merges when ready.

## Rules

1. **Default to stateless.** Most workflows (triage, review, checks) don't need memory.
2. **Use issues for daily tracking.** The `daily-repo-status` pattern (57 repos) proves this works at scale.
3. **Use discussions for reports.** Threaded, searchable, community-visible.
4. **Use repo-memory for learned knowledge.** If the agent discovers patterns, commit them as config.
5. **Use branches for iterative work.** Daily improvers that accumulate changes over multiple runs.
6. **Don't over-engineer state.** If you need a database, you're probably building an app, not a workflow.
