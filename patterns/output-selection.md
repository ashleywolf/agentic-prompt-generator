# Output Selection

> **"Where should results go?"**

## The Numbers

From **679 workflows** across **269 repos**, workflows produce output through several mechanisms. The scan tracks `safe_outputs` declarations (explicit output type restrictions) but most workflows use the platform defaults.

| Output Type | Description | When to Use |
|-------------|-------------|-------------|
| `add-comment` | Comment on the triggering issue/PR | Feedback, triage results, analysis |
| `add-labels` | Apply labels to issues/PRs | Classification, triage |
| `create-pull-request` | Open a new PR with changes | Code fixes, doc updates |
| `create-issue` | File a new issue | Findings from scheduled scans |
| `create-discussion` | Post to Discussions | Reports, summaries |
| `dispatch-workflow` | Trigger another workflow | Chaining, orchestration |
| `upload-asset` | Upload files | Reports, artifacts |
| `noop` | No output (dry run) | Testing, validation |

## Decision Table

| Your workflow does… | Best output | Why |
|---------------------|-------------|-----|
| Issue triage | `add-comment` + `add-labels` | Respond inline, classify |
| Daily status report | `create-issue` or `create-discussion` | Persistent, searchable |
| CI failure diagnosis | `add-comment` | Comment on the failing PR/issue |
| Code improvement | `create-pull-request` | Propose changes for review |
| Spam/moderation check | `add-labels` | Fast, automatable |
| Research/analysis | `create-discussion` | Long-form, threaded |
| Pipeline orchestration | `dispatch-workflow` | Chain workflows together |

## Pattern 1: Comment + Labels (Issue Triage)

The most common output pattern. Agent reads an issue, adds a comment with analysis, and applies labels.

**Real examples:**
- [`appwrite/appwrite/issue-triage`](https://github.com/appwrite/appwrite/blob/main/.github/workflows/issue-triage.md) — Labels + comment on every issue (54,898 ⭐)
- [`apolloconfig/apollo/issue-triage`](https://github.com/apolloconfig/apollo/blob/main/.github/workflows/issue-triage.md) — Categorize and label (29,779 ⭐)
- [`evcc-io/evcc/triage-agent`](https://github.com/evcc-io/evcc/blob/main/.github/workflows/triage-agent.md) — Triage with labels (6,169 ⭐)
- [`foxminchan/BookWorm/issue-triage`](https://github.com/foxminchan/BookWorm/blob/main/.github/workflows/issue-triage.md) — Label and categorize (475 ⭐)

## Pattern 2: Create PR (Code Changes)

Agent makes code changes and opens a PR for human review.

**Real examples:**
- [`BabylonJS/Babylon.js/code-simplifier`](https://github.com/BabylonJS/Babylon.js/blob/main/.github/workflows/code-simplifier.md) — Simplifies code, opens PR (25,113 ⭐)
- [`RustPython/RustPython/upgrade-pylib`](https://github.com/RustPython/RustPython/blob/main/.github/workflows/upgrade-pylib.md) — Upgrades Python lib, opens PR (21,810 ⭐)
- [`ohcnetwork/care_fe/daily-playwright-improver`](https://github.com/ohcnetwork/care_fe/blob/main/.github/workflows/daily-playwright-improver.md) — Improves tests, submits PR (606 ⭐)
- [`kaito-project/aikit/daily-test-improver`](https://github.com/kaito-project/aikit/blob/main/.github/workflows/daily-test-improver.md) — Test improvements as PRs (509 ⭐)

## Pattern 3: Create Issue (Scheduled Findings)

Scheduled workflows that discover issues and file them for humans.

**Real examples:**
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) — Daily health report as issue (23,180 ⭐)
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) — Status posted as issue (5,457 ⭐)
- [`erigontech/erigon/daily-repo-status`](https://github.com/erigontech/erigon/blob/main/.github/workflows/daily-repo-status.md) — Daily status issue (3,531 ⭐)

## Pattern 4: Create Discussion (Reports & Analysis)

Long-form output that benefits from threaded responses.

**Real examples:**
- [`github/gh-aw/lockfile-stats`](https://github.com/github/gh-aw/blob/main/.github/workflows/lockfile-stats.md) — Posts analysis to Discussions (3,356 ⭐). This workflow declares `safe_outputs: [create-pull-request, create-discussion, add-comment, create-issue]` — one of few with explicit output restrictions.

## Pattern 5: Safe Outputs (Restricting What the Agent Can Do)

The `safe_outputs` field restricts which output types a workflow is allowed to use. Only 3 workflows in the scan declare explicit `safe_outputs`:

- [`github/gh-aw/lockfile-stats`](https://github.com/github/gh-aw/blob/main/.github/workflows/lockfile-stats.md) — `[create-pull-request, create-discussion, add-comment, create-issue]` (3,356 ⭐)
- [`JoshGreenslade/AITraining/workflow-architect`](https://github.com/JoshGreenslade/AITraining/blob/main/.github/workflows/workflow-architect.md) — `[add-comment, add-labels]`
- [`nikhilmlal/test_repo/issue-triage.agent`](https://github.com/nikhilmlal/test_repo/blob/main/.github/workflows/issue-triage.agent.md) — `[add-comment]`

**Most workflows rely on the platform's default output permissions.** Use `safe_outputs` when you need to lock down a workflow to only specific actions.

## Rules

1. **Issue triage → `add-comment` + `add-labels`.** This is the standard pattern across 41 triage workflows.
2. **Code changes → `create-pull-request`.** Never push directly; always go through PR review.
3. **Daily reports → `create-issue` or `create-discussion`.** Issues are more visible; discussions allow threads.
4. **Use `safe_outputs` to restrict high-risk workflows.** Especially workflows that run on untrusted input (issues from public).
5. **Chain workflows with `dispatch-workflow`** when one agent's output feeds another.
6. **Start with minimal outputs** — you can always add more later. It's harder to restrict after the fact.
