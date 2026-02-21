# Trigger Selection

> **"When should my workflow run?"**

## The Numbers

From **679 workflows** across **269 repos** (workflows can have multiple triggers):

| Trigger | Count | Share | Use Case |
|---------|-------|-------|----------|
| `issues` | 467 | 69% | React to new/updated issues |
| `workflow_dispatch` | 467 | 69% | Manual runs, testing |
| `schedule` | 395 | 58% | Cron-based recurring work |
| `pull_request` | 102 | 15% | PR review, validation |
| `discussion` | 75 | 11% | Community Q&A, support |
| `push` | 57 | 8% | Post-merge automation |
| `slash_command` | 35 | 5% | On-demand via comments |
| `workflow_run` | 21 | 3% | Chain after CI completion |

## Decision Table

| You want to… | Trigger | Common pairing |
|--------------|---------|----------------|
| Triage incoming issues | `issues` + `workflow_dispatch` | The dominant pattern (467 workflows) |
| Run daily maintenance | `schedule` + `workflow_dispatch` | Add dispatch for manual re-runs |
| Review PRs | `pull_request` | Often standalone |
| Respond to CI failures | `workflow_run` | Runs after another workflow completes |
| Let users invoke on-demand | `slash_command` | Via issue/PR comments |
| Monitor discussions | `discussion` | Q&A, support triage |
| React to merges | `push` | Post-merge cleanup, releases |

## Pattern 1: Issue-Triggered (467 workflows)

The most common trigger. Nearly always paired with `workflow_dispatch` for testing.

**Real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — Triages every new issue (54,898 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) — Labels and categorizes issues (29,779 ⭐)
- [`evcc-io/evcc/triage-agent`](https://github.com/evcc-io/evcc/blob/main/.github/workflows/triage-agent.md) — Issue + PR triage (6,169 ⭐)
- [`frankbria/ralph-claude-code/triage-incoming-issues`](https://github.com/frankbria/ralph-claude-code/blob/main/.github/workflows/triage-incoming-issues.md) — Incoming issue routing (7,097 ⭐)

## Pattern 2: Schedule-Based (395 workflows)

Cron triggers for recurring work. Almost always paired with `workflow_dispatch`.

**Real examples:**
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) — Daily health report (23,180 ⭐)
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) — Daily status with discussion trigger too (5,457 ⭐)
- [`erigontech/erigon/daily-repo-status`](https://github.com/erigontech/erigon/blob/main/.github/workflows/daily-repo-status.md) — Daily repo health (3,531 ⭐)
- [`BabylonJS/Babylon.js/code-simplifier`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/workflows/code-simplifier.md) — Scheduled code improvement (25,113 ⭐)

The `daily-repo-status` pattern appears in **57 repos** — the single most common workflow name in the scan.

## Pattern 3: Pull Request (102 workflows)

Triggered on PR open/update. Used for review, validation, and checks.

**Real examples:**
- [`f/prompts.chat/spam-check`](https://github.com/f/prompts.chat/blob/main/.github/workflows/spam-check.md) — Checks PRs for spam content (145,906 ⭐)
- [`github/copilot-sdk/sdk-consistency-review`](https://github.com/github/copilot-sdk/blob/main/.github/workflows/sdk-consistency-review.md) — SDK consistency on PRs (7,254 ⭐)
- [`ZSWatch/ZSWatch/docs-pr-analyze`](https://github.com/ZSWatch/ZSWatch/blob/main/.github/workflows/docs-pr-analyze.md) — Analyzes docs PRs (3,128 ⭐)
- [`llm-d/llm-d/link-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/link-checker.md) — Checks links in PRs (2,516 ⭐)
- [`llm-d/llm-d/typo-checker`](https://github.com/llm-d/llm-d/blob/main/.github/workflows/typo-checker.md) — Checks typos in PRs (2,516 ⭐)

## Pattern 4: Workflow Run (21 workflows)

Chains after another workflow completes. The dominant use case is **CI Doctor** — diagnosing CI failures.

**Real examples:**
- [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) — Diagnoses CI failures after `workflow_run` (21,566 ⭐)
- [`devantler-tech/ksail/ci-doctor`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/ci-doctor.md) — CI failure analysis (130 ⭐)
- [`sayinmehmet47/kitapKurdu/ci-doctor`](https://github.com/sayinmehmet47/kitapKurdu/blob/main/.github/workflows/ci-doctor.md) — CI doctor pattern (17 ⭐)

All 16 `ci-doctor` workflows in the scan use `workflow_run` to trigger after CI.

## Pattern 5: Discussion-Triggered (75 workflows)

Responds to GitHub Discussions — Q&A, support, community engagement.

**Real examples:**
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) — Also monitors discussions (5,457 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Discussions can request test improvements (509 ⭐)
- [`devantler-tech/ksail/unbloat-docs`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/unbloat-docs.md) — Discussion-triggered doc cleanup (130 ⭐)

## Pattern 6: Slash Command (35 workflows)

On-demand invocation via comment commands. Used for interactive tools.

**Real examples:**
- [`github/gh-aw/q`](https://github.com/github/gh-aw/blob/main/.github/workflows/q.md) — Answer questions on-demand (3,356 ⭐)
- [`github/gh-aw/scout`](https://github.com/github/gh-aw/blob/main/.github/workflows/scout.md) — On-demand code search (3,356 ⭐)
- [`github/gh-aw/grumpy-reviewer`](https://github.com/github/gh-aw/blob/main/.github/workflows/grumpy-reviewer.md) — Request a review on-demand (3,356 ⭐)
- [`devantler-tech/ksail/pr-fix`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/pr-fix.md) — Fix PR issues on-demand (130 ⭐)

## Pattern 7: Push-Triggered (57 workflows)

Runs after pushes to specific branches. Used for post-merge automation.

**Real examples:**
- [`phpstan/phpstan-src/document-config-params`](https://github.com/phpstan/phpstan-src/blob/main/.github/workflows/document-config-params.md) — Updates docs after code push (385 ⭐)
- [`github/gh-aw/release`](https://github.com/github/gh-aw/blob/main/.github/workflows/release.md) — Release automation on push (3,356 ⭐)
- [`pikax/verter/update-docs`](https://github.com/pikax/verter/blob/main/.github/workflows/update-docs.md) — Auto-update docs on push (54 ⭐)

## Common Trigger Combinations

| Combination | Count | Pattern |
|-------------|-------|---------|
| `issues` + `workflow_dispatch` | ~400+ | Issue triage with manual testing |
| `schedule` + `workflow_dispatch` | ~350+ | Daily/weekly jobs with manual re-run |
| `schedule` + `issues` + `workflow_dispatch` | ~200+ | Multi-purpose: react + recurring |
| `pull_request` alone | ~50 | Pure PR review |
| `workflow_run` alone | ~16 | CI Doctor pattern |

## Rules

1. **Always include `workflow_dispatch`** alongside your primary trigger. You'll need it for testing and manual re-runs.
2. **Issue triage = `issues` trigger.** It's the #1 pattern by a wide margin.
3. **Daily jobs = `schedule` + `workflow_dispatch`.** The 57 `daily-repo-status` instances prove this.
4. **CI diagnosis = `workflow_run`.** All 16 `ci-doctor` workflows chain off CI completion.
5. **Use `discussion` alongside `issues`** if your project uses Discussions for support.
6. **Use `slash_command` for interactive tools** — Q&A bots, on-demand reviews, search.
7. **Use `push` sparingly** — it triggers on every push. Best for post-merge automation on main/release branches.
