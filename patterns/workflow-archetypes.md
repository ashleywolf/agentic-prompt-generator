# Workflow Archetypes

> **"What type am I building?"**

## The Numbers

From **679 workflows** across **269 repos**, clear archetypes emerge from naming patterns and trigger configurations:

| Archetype | Workflows | Repos | Defining Feature |
|-----------|-----------|-------|------------------|
| Issue Triage | 41 | 40 | `issues` trigger, labels + comments |
| Daily Improver | 155 | 102 | `schedule` trigger, code changes |
| CI Doctor | 16 | 16 | `workflow_run` trigger, failure analysis |
| Weekly Report | 35 | 31 | `schedule` trigger, summary output |
| Slash Command | 35 | ~10 | `slash_command` trigger, on-demand |
| PR Reviewer | ~50 | ~40 | `pull_request` trigger, review comments |
| Moderation | 2 | 2 | Content policy enforcement |
| Upstream Monitor | 11 | ~10 | `schedule`, watches dependencies |

---

## Archetype 1: Issue Triage (41 workflows, 40 repos)

**What it does:** Reads new issues, classifies them, applies labels, and optionally comments with guidance.

**Triggers:** `issues` + `workflow_dispatch`
**Output:** `add-labels` + `add-comment`
**Model:** Default (no explicit model needed)

**Top real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) (54,898 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) (29,779 ⭐)
- [`github/copilot-sdk/issue-triage`](https://github.com/github/copilot-sdk/blob/main/.github/workflows/issue-triage.md) (7,254 ⭐)
- [`frankbria/ralph-claude-code/triage-incoming-issues`](https://github.com/frankbria/ralph-claude-code/blob/main/.github/workflows/triage-incoming-issues.md) (7,097 ⭐)
- [`evcc-io/evcc/triage-agent`](https://github.com/evcc-io/evcc/blob/main/.github/workflows/triage-agent.md) (6,169 ⭐)
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) (5,457 ⭐)
- [`apache/cloudstack/issue-triage-agent`](https://github.com/apache/cloudstack/blob/main/.github/workflows/issue-triage-agent.md) (2,800 ⭐)
- [`opencollective/opencollective/issue-triage-agent`](https://github.com/opencollective/opencollective/blob/main/.github/workflows/issue-triage-agent.md) (2,248 ⭐)
- [`apollographql/rover/issue-triage`](https://github.com/apollographql/rover/blob/main/.github/workflows/issue-triage.md) (444 ⭐)

**Pattern notes:**
- The most popular archetype by repo adoption
- Most use default model — classification doesn't need expensive models
- Often paired with `stop_after: +30d` for long-running triage windows

---

## Archetype 2: Daily Improver (155 workflows, 102 repos)

**What it does:** Runs on a schedule, finds something to improve, and submits a PR.

**Triggers:** `schedule` + `workflow_dispatch`
**Output:** `create-pull-request`
**Model:** Default or `gpt-5.1-codex-mini`
**Pre-steps:** Often yes (run tests/linters first)

**Sub-variants:**

### Daily Repo Status (57 repos)
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) (23,180 ⭐)
- [`erigontech/erigon/daily-repo-status`](https://github.com/erigontech/erigon/blob/main/.github/workflows/daily-repo-status.md) (3,531 ⭐)
- [`apache/cloudstack/daily-repo-status`](https://github.com/apache/cloudstack/blob/main/.github/workflows/daily-repo-status.md) (2,800 ⭐)
- [`foxminchan/BookWorm/daily-repo-status`](https://github.com/foxminchan/BookWorm/blob/main/.github/workflows/daily-repo-status.md) (475 ⭐)
- [`javaevolved/javaevolved.github.io/daily-repo-status`](https://github.com/javaevolved/javaevolved.github.io/blob/main/.github/workflows/daily-repo-status.md) (152 ⭐)

### Daily Test Improver (13 repos)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) (509 ⭐)
- [`lablup/backend.ai-webui/daily-test-improver`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/daily-test-improver.md) (125 ⭐)
- [`talk2MeGooseman/stream_closed_captioner_phoenix/daily-test-improver`](https://github.com/talk2MeGooseman/stream_closed_captioner_phoenix/blob/main/.github/workflows/daily-test-improver.md) (24 ⭐)

### Daily Performance Improver (9 repos)
- [`devantler-tech/ksail/daily-perf-improver`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/daily-perf-improver.md) (130 ⭐)
- [`fslaborg/FsMath/daily-perf-improver`](https://github.com/fslaborg/FsMath/blob/main/.github/workflows/daily-perf-improver.md) (17 ⭐)
- [`iamnbutler/sol-ui/daily-perf-improver`](https://github.com/iamnbutler/sol-ui/blob/main/.github/workflows/daily-perf-improver.md) (11 ⭐)

### Code Simplifier (13 repos)
- [`BabylonJS/Babylon.js/code-simplifier`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/workflows/code-simplifier.md) (25,113 ⭐)
- [`devantler-tech/ksail/daily-code-simplifier`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/daily-code-simplifier.md) (130 ⭐)
- [`Kong/kongctl/code-simplifier`](https://github.com/Kong/kongctl/blob/main/.github/workflows/code-simplifier.md) (12 ⭐)

---

## Archetype 3: CI Doctor (16 workflows, 16 repos)

**What it does:** Triggers after a CI workflow fails, analyzes the failure, and comments with a diagnosis.

**Triggers:** `workflow_run`
**Output:** `add-comment` on the failing PR/issue
**Model:** Default or `gpt-5.1-codex-mini`

**Real examples:**
- [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) — Uses `claude-sonnet-4.5` (21,566 ⭐)
- [`devantler-tech/ksail/ci-doctor`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/ci-doctor.md) (130 ⭐)
- [`tosin2013/mcp-adr-analysis-server/ci-doctor`](https://github.com/tosin2013/mcp-adr-analysis-server/blob/main/.github/workflows/ci-doctor.md) (19 ⭐)
- [`sayinmehmet47/kitapKurdu/ci-doctor`](https://github.com/sayinmehmet47/kitapKurdu/blob/main/.github/workflows/ci-doctor.md) (17 ⭐)
- [`ianlintner/rust-oauth2-server/ci-doctor`](https://github.com/ianlintner/rust-oauth2-server/blob/main/.github/workflows/ci-doctor.md) — Uses `gpt-5.1-codex-mini` (3 ⭐)

**Pattern notes:**
- `workflow_run` is the defining trigger — it chains after CI completion
- All 16 instances follow the same name (`ci-doctor`) or close variant (`workflow-doctor`)
- Low barrier to adopt: just add the workflow file and point it at your CI

---

## Archetype 4: Weekly Report (35 workflows, 31 repos)

**What it does:** Runs weekly to generate summaries, research digests, or status reports.

**Triggers:** `schedule` + `workflow_dispatch`
**Output:** `create-issue` or `create-discussion`
**Model:** Default

**Real examples:**
- [`github/gh-aw/weekly-issue-summary`](https://github.com/github/gh-aw/blob/main/.github/workflows/weekly-issue-summary.md) (3,356 ⭐)
- [`devantler-tech/ksail/weekly-research`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/weekly-research.md) (130 ⭐)
- [`lablup/backend.ai-webui/weekly-team-status`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/weekly-team-status.md) (125 ⭐)
- [`devantler-tech/ksail/weekly-promote-ksail`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/weekly-promote-ksail.md) (130 ⭐)

**Sub-variants:**
- `weekly-research` (17 repos) — Researches topics and creates digests
- `weekly-team-status` — Team activity summaries
- `weekly-promote-*` — Community outreach automation

---

## Archetype 5: Slash Command (35 workflows)

**What it does:** Responds to on-demand commands in issue/PR comments.

**Triggers:** `slash_command` (sometimes + `issues`)
**Output:** `add-comment`
**Model:** Varies

**Real examples:**
- [`github/gh-aw/q`](https://github.com/github/gh-aw/blob/main/.github/workflows/q.md) — Answer questions (3,356 ⭐)
- [`github/gh-aw/scout`](https://github.com/github/gh-aw/blob/main/.github/workflows/scout.md) — Code search (3,356 ⭐)
- [`github/gh-aw/grumpy-reviewer`](https://github.com/github/gh-aw/blob/main/.github/workflows/grumpy-reviewer.md) — On-demand code review (3,356 ⭐)
- [`github/gh-aw/archie`](https://github.com/github/gh-aw/blob/main/.github/workflows/archie.md) — Architecture analysis (3,356 ⭐)
- [`github/gh-aw/plan`](https://github.com/github/gh-aw/blob/main/.github/workflows/plan.md) — Planning assistant (3,356 ⭐)
- [`devantler-tech/ksail/pr-fix`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/pr-fix.md) — Fix PR issues on request (130 ⭐)

---

## Archetype 6: PR Reviewer (~50 workflows)

**What it does:** Reviews pull requests for quality, consistency, or specific checks.

**Triggers:** `pull_request`
**Output:** `add-comment` (review comments)
**Model:** Default or `claude-sonnet`

**Real examples:**
- [`f/prompts.chat/spam-check`](https://github.com/f/prompts.chat/blob/main/.github/workflows/spam-check.md) — Spam detection on PRs (145,906 ⭐)
- [`github/copilot-sdk/sdk-consistency-review`](https://github.com/github/copilot-sdk/blob/main/.github/workflows/sdk-consistency-review.md) — SDK consistency (7,254 ⭐)
- [`ZSWatch/ZSWatch/docs-pr-analyze`](https://github.com/ZSWatch/ZSWatch/blob/main/.github/workflows/docs-pr-analyze.md) — Docs PR analysis (3,128 ⭐)
- [`llm-d/llm-d/link-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/link-checker.md) — Link validation (2,516 ⭐)
- [`llm-d/llm-d/typo-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/typo-checker.md) — Typo detection (2,516 ⭐)
- [`elastic/opentelemetry-collector-components/pr-review`](https://github.com/elastic/opentelemetry-collector-components/blob/main/.github/workflows/pr-review.md) — Deep review with `claude-opus-4.6` (16 ⭐)
- [`wp-media/wp-rocket/pr-release-doc-generator`](https://github.com/wp-media/wp-rocket/blob/main/.github/workflows/pr-release-doc-generator.md) — Release doc generation on PR (738 ⭐)

---

## Archetype 7: Moderation (2 workflows)

**What it does:** Enforces content policies on issues and PRs.

**Triggers:** `issues` + `pull_request`
**Output:** `add-labels`, moderation actions
**Model:** Default

**Real examples:**
- [`f/prompts.chat/spam-check`](https://github.com/f/prompts.chat/blob/main/.github/workflows/spam-check.md) — Checks for spam in PRs/issues (145,906 ⭐)
- [`github/gh-aw/ai-moderator`](https://github.com/github/gh-aw/blob/main/.github/workflows/ai-moderator.md) — AI-powered content moderation (3,356 ⭐)

**Pattern notes:**
- Rare but impactful — `f/prompts.chat` is the highest-starred repo in the entire scan
- Critical for high-traffic public repos

---

## Archetype 8: Upstream Monitor (11 repos)

**What it does:** Watches upstream dependencies for changes and alerts or auto-updates.

**Triggers:** `schedule` + `workflow_dispatch`
**Output:** `create-issue` or `create-pull-request`
**Model:** Default

**Real examples:**
- [`npgsql/efcore.pg/sync-to-latest-ef`](https://github.com/npgsql/efcore.pg/blob/main/.github/workflows/sync-to-latest-ef.md) — Syncs to upstream EF Core (1,801 ⭐)
- [`llm-d/llm-d-kv-cache/upstream-monitor`](https://github.com/llm-d/llm-d-kv-cache/blob/main/.github/workflows/upstream-monitor.md) — Monitors upstream changes (103 ⭐)
- [`llm-d/llm-d-inference-sim/upstream-monitor`](https://github.com/llm-d/llm-d-inference-sim/blob/main/.github/workflows/upstream-monitor.md) — Upstream dependency tracking (87 ⭐)
- [`drehelis/gcp-emulator-ui/check-emulator-updates`](https://github.com/drehelis/gcp-emulator-ui/blob/main/.github/workflows/check-emulator-updates.md) — Checks GCP emulator releases (35 ⭐)

---

## Quick Reference: Which Archetype Am I?

| I want to… | Archetype | Start from |
|-------------|-----------|------------|
| Label and classify issues | **Issue Triage** | `appwrite/appwrite/issue-triage` |
| Run daily code improvements | **Daily Improver** | `BabylonJS/Babylon.js/code-simplifier` |
| Diagnose CI failures | **CI Doctor** | `JanDeDobbeleer/oh-my-posh/workflow-doctor` |
| Generate weekly summaries | **Weekly Report** | `devantler-tech/ksail/weekly-research` |
| Add on-demand commands | **Slash Command** | `github/gh-aw/q` |
| Review PRs automatically | **PR Reviewer** | `github/copilot-sdk/sdk-consistency-review` |
| Moderate content | **Moderation** | `f/prompts.chat/spam-check` |
| Watch upstream deps | **Upstream Monitor** | `npgsql/efcore.pg/sync-to-latest-ef` |

## Rules

1. **Pick one archetype to start.** Don't combine them in a single workflow.
2. **Issue Triage is the easiest to adopt** — 40 repos prove it works.
3. **Daily Improver is the most popular** — 102 repos use some variant.
4. **CI Doctor has the highest consistency** — all 16 use `workflow_run` trigger.
5. **Name your workflow after the archetype** — `issue-triage`, `ci-doctor`, `daily-repo-status`. It signals intent to anyone reading your repo.
6. **Build a suite, not a monolith** — `devantler-tech/ksail` runs 14 separate workflows, each with one job.
