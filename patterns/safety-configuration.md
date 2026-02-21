# Safety Configuration

> **"How do I lock it down?"**

## The Numbers

From **679 workflows** across **269 repos**:

| Safety Feature | Count | Share |
|----------------|-------|-------|
| `stop_after` (time limit) | 61 | 9% |
| `safe_outputs` (output restriction) | 3 | 0.4% |

### `stop_after` Distribution

| Duration | Count |
|----------|-------|
| `+1mo` | 24 |
| `+30d` | 18 |
| `+48h` | 16 |
| `+6mo` | 2 |
| `+10d` | 1 |

91% of workflows use no explicit time limit or output restriction. Safety configuration is an opt-in layer for specific risk scenarios.

## Decision Table

| Risk | Mitigation | Why |
|------|------------|-----|
| Agent runs too long | `stop_after` | Prevent runaway compute costs |
| Agent writes to wrong places | `safe_outputs` | Restrict output types |
| Agent accesses external APIs | `network.allowed` | Whitelist domains |
| Agent does too much too fast | Rate limiting | Prevent flooding |
| Untrusted input (public issues) | Output restriction + review | Don't auto-merge |

## Safety Feature 1: `stop_after` (61 workflows)

Sets a maximum lifetime for the workflow. After this duration, the workflow is terminated regardless of state.

### `+48h` — Short Tasks (16 workflows)

Used for workflows that should complete quickly. If they're still running after 48 hours, something is wrong.

**Real examples:**
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Test improvements should finish quickly (509 ⭐)
- [`fslaborg/FsMath/daily-perf-improver`](https://github.com/fslaborg/FsMath/blob/main/.github/workflows/daily-perf-improver.md) — Performance work with tight deadline (17 ⭐)
- [`iamnbutler/sol-ui/daily-perf-improver`](https://github.com/iamnbutler/sol-ui/blob/main/.github/workflows/daily-perf-improver.md) — Daily perf tasks, 48h cap (11 ⭐)
- [`danielmeppiel/agentic-hike-planner/daily-test-improver`](https://github.com/danielmeppiel/agentic-hike-planner/blob/main/.github/workflows/daily-test-improver.md) — Test improvements with tight timeout (6 ⭐)

### `+30d` / `+1mo` — Long-Running Tasks (42 workflows)

Used for workflows that may need extended time — waiting for human review, multi-step processes.

**Real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — 30-day timeout for triage (54,898 ⭐)
- [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) — 1-month timeout for CI diagnosis (21,566 ⭐)
- [`opencollective/opencollective/issue-triage-agent`](https://github.com/opencollective/opencollective/blob/main/.github/workflows/issue-triage-agent.md) — Monthly triage window (2,248 ⭐)
- [`kaito-project/aikit/issue-triage`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/issue-triage.md) — 30-day triage window (509 ⭐)
- [`chrisreddington/flight-school/issue-triage`](https://github.com/chrisreddington/flight-school/blob/main/.github/workflows/issue-triage.md) — 1-month triage window (24 ⭐)
- [`talk2MeGooseman/stream_closed_captioner_phoenix/daily-test-improver`](https://github.com/talk2MeGooseman/stream_closed_captioner_phoenix/blob/main/.github/workflows/daily-test-improver.md) — Monthly timeout for test improvements (24 ⭐)

### `+6mo` — Extended Projects (2 workflows)

Rare. Used for long-term tracking workflows.

- [`lablup/backend.ai-webui/weekly-team-status`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/weekly-team-status.md) — 6-month window for team tracking (125 ⭐)
- [`lablup/backend.ai-webui/daily-test-improver`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/daily-test-improver.md) — 6-month window for iterative test improvement (125 ⭐)

## Safety Feature 2: `safe_outputs` (3 workflows)

Explicitly restricts which output types the workflow is allowed to produce. Acts as a whitelist.

**Real examples:**
- [`JoshGreenslade/AITraining/workflow-architect`](https://github.com/JoshGreenslade/AITraining/blob/main/.github/workflows/workflow-architect.md) — `[add-comment, add-labels]` — can only comment and label, not create PRs
- [`nikhilmlal/test_repo/issue-triage.agent`](https://github.com/nikhilmlal/test_repo/blob/main/.github/workflows/issue-triage.agent.md) — `[add-comment]` — comment-only, most restrictive

See also: [`github/gh-aw/lockfile-stats`](https://github.com/github/gh-aw/blob/main/.github/workflows/lockfile-stats.md) uses `[create-pull-request, create-discussion, add-comment, create-issue]` — a broad but explicit output whitelist.

**Use `safe_outputs` when:**
- The workflow runs on untrusted input (public issues, PRs from forks)
- You want to prevent the agent from creating PRs, issues, or discussions
- The workflow should only observe and comment, not modify

## Safety Feature 3: Network Restrictions

Use `network.allowed` to whitelist which external domains the agent can access. Not widely tracked in the scan, but important for:
- Workflows that call external APIs
- Preventing data exfiltration
- Ensuring the agent only talks to approved services

## Safety Feature 4: Engine Selection

From the scan, **170 workflows** explicitly use `engine: copilot`, **46 use `claude`**, and **14 use `codex`**. Engine selection affects safety boundaries — each engine has different default permissions and capabilities.

## Workflows with Multiple Safety Features

Some workflows combine safety measures:

- [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) — `stop_after: +1mo` + explicit model selection + `workflow_run` trigger (only runs after CI) (21,566 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — `stop_after: +48h` + pre-steps (controlled input) (509 ⭐)
- [`lablup/backend.ai-webui/daily-test-improver`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/daily-test-improver.md) — `stop_after: +6mo` + pre-steps + discussion trigger (125 ⭐)

## Rules

1. **Always set `stop_after`** on scheduled workflows. Without it, a stuck workflow runs indefinitely.
2. **Use `+48h` for daily jobs** that should complete within a day.
3. **Use `+30d` for triage workflows** that may need human interaction over weeks.
4. **Use `safe_outputs` on public-facing workflows** — restrict what untrusted input can trigger.
5. **Restrict to `[add-comment]` for read-only workflows** — the most conservative setting.
6. **Combine safety features** — `stop_after` + `safe_outputs` + network restrictions for maximum lockdown.
7. **Start permissive, tighten as needed** — or start restrictive and open up. Both approaches work; pick one and be consistent.
8. **The 91% without safety config aren't necessarily unsafe** — platform defaults provide baseline protections. Explicit config is for workflows with higher risk profiles.
