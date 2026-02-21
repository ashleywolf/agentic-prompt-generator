# Data Ingestion

> **"How do I feed data to my workflow?"**

## The Numbers

From scanning **269 repos** with **661 source-available workflows**:

| Pattern | Count | Share |
|---------|-------|-------|
| No pre-steps (agent-direct) | 565 | 85% |
| Pre-steps | 96 | 15% |

Most workflows let the agent gather its own data. Pre-steps are reserved for cases where the agent can't reach the data directly, or where pre-processing saves significant tokens.

## Decision Table

| Situation | Pattern | Why |
|-----------|---------|-----|
| Agent can read the repo directly | **Agent-direct** | Simpler, no data staleness |
| Data lives outside the repo (API, DB) | **Pre-step bash/python** | Fetch and pipe to agent |
| Repo is large (>1GB) | **Sparse checkout** | Reduce clone time |
| Data needs transformation before analysis | **Pre-step python** | Clean/reshape first |
| Multiple data sources needed | **Pre-step bash** | Aggregate into one context |

## Pattern 1: Agent-Direct (565/661 workflows)

The agent reads files, issues, and PRs itself using built-in tools. No pre-processing.

**Real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — Agent reads the incoming issue directly (54,898 ⭐)
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) — Agent queries repo state on its own (23,180 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) — No pre-processing, agent reads the issue (29,779 ⭐)

**When to use:** The data is already in the repo (code, issues, PRs, discussions) and doesn't need transformation.

## Pattern 2: Pre-Step Bash (fetching external data)

A `pre-steps` block runs shell commands before the agent starts. Output is piped as context.

**Real examples:**
- [`github/gh-aw/daily-copilot-token-report`](https://github.com/github/gh-aw/blob/main/.github/workflows/daily-copilot-token-report.md) — Fetches token usage data via API before analysis (3,356 ⭐)
- [`github/gh-aw/bot-detection`](https://github.com/github/gh-aw/blob/main/.github/workflows/bot-detection.md) — Gathers activity signals in pre-step (3,356 ⭐)
- [`github/gh-aw/stale-repo-identifier`](https://github.com/github/gh-aw/blob/main/.github/workflows/stale-repo-identifier.md) — Collects repo metadata before agent evaluates (3,356 ⭐)

## Pattern 3: Pre-Step Python (data transformation)

Uses Python to reshape or aggregate data before the agent sees it.

**Real examples:**
- [`github/gh-aw/prompt-clustering-analysis`](https://github.com/github/gh-aw/blob/main/.github/workflows/prompt-clustering-analysis.md) — Python clusters prompts before agent analyzes patterns (3,356 ⭐)
- [`github/gh-aw/static-analysis-report`](https://github.com/github/gh-aw/blob/main/.github/workflows/static-analysis-report.md) — Runs static analysis tools, feeds results to agent (3,356 ⭐)
- [`kubestellar/docs/maintainer-metrics`](https://github.com/kubestellar/docs/blob/main/.github/workflows/maintainer-metrics.md) — Computes contributor metrics in pre-step (23 ⭐)

## Pattern 4: Pre-Steps in Community Repos

Pre-steps aren't just for large orgs. Community repos use them too:

- [`fsprojects/FSharp.Data/auto-maintainer-assistant`](https://github.com/fsprojects/FSharp.Data/blob/main/.github/workflows/auto-maintainer-assistant.md) — Pre-step gathers NuGet package state (864 ⭐)
- [`ohcnetwork/care_fe/daily-playwright-improver`](https://github.com/ohcnetwork/care_fe/blob/main/.github/workflows/daily-playwright-improver.md) — Runs Playwright tests, feeds failures to agent (606 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Runs test suite in pre-step, agent improves failures (509 ⭐)
- [`learntocloud/learn-to-cloud-app/content-link-auditor`](https://github.com/learntocloud/learn-to-cloud-app/blob/main/.github/workflows/content-link-auditor.md) — Checks links in pre-step, agent fixes broken ones (93 ⭐)

## Rules

1. **Default to agent-direct.** 85% of workflows do. Don't add pre-steps unless you have a reason.
2. **Use pre-steps when the agent can't reach the data** — external APIs, databases, or tool output (test results, linter output).
3. **Use pre-steps to save tokens** — if raw data is huge, pre-process it down to what matters.
4. **Keep pre-steps idempotent** — they should produce the same output given the same inputs.
5. **Pre-step output becomes agent context** — keep it structured (JSON, markdown tables) so the agent can parse it.
