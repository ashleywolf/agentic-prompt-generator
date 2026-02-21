# Shared Components

> **"How do I reuse logic?"**

## The Numbers

From **269 repos** with **679 workflows**, most workflows are self-contained. Reuse patterns are emerging but still uncommon:

| Pattern | Examples | Description |
|---------|----------|-------------|
| Naming conventions | 57 repos use `daily-repo-status` | Same workflow name = same logic |
| Multi-workflow repos | `github/gh-aw` has 120 workflows | Shared context via co-location |
| Imports | 7 workflows declare `imports` | Explicit dependency on shared code |
| Fork-and-customize | 16 repos have `ci-doctor` | Community copies of proven patterns |

## Decision Table

| You want to… | Pattern | Example |
|--------------|---------|---------|
| Use a proven workflow pattern | **Fork a template** | Copy `daily-repo-status` from any of 57 repos |
| Share config across workflows | **Shared directory** | `github/gh-aw` shared/ pattern |
| Import shared logic | **Imports field** | `Olino3/forge` imports pattern |
| Standardize across many repos | **Naming convention** | Same workflow name = same behavior |
| Build a workflow suite | **Multi-workflow repo** | `devantler-tech/ksail` (14 workflows) |

## Pattern 1: Fork-and-Customize (Most Common)

The most popular "reuse" pattern: copy a proven workflow and customize it.

### `daily-repo-status` — 57 repos

The single most copied workflow. Generates daily health reports.

**Examples using this exact pattern:**
- [`dotnet/maui/daily-repo-status`](https://github.com/dotnet/maui/blob/main/.github/workflows/daily-repo-status.md) (23,180 ⭐)
- [`dotnet/aspire/daily-repo-status`](https://github.com/dotnet/aspire/blob/main/.github/workflows/daily-repo-status.md) (5,457 ⭐)
- [`erigontech/erigon/daily-repo-status`](https://github.com/erigontech/erigon/blob/main/.github/workflows/daily-repo-status.md) (3,531 ⭐)
- [`apache/cloudstack/daily-repo-status`](https://github.com/apache/cloudstack/blob/main/.github/workflows/daily-repo-status.md) (2,800 ⭐)
- [`foxminchan/BookWorm/daily-repo-status`](https://github.com/foxminchan/BookWorm/blob/main/.github/workflows/daily-repo-status.md) (475 ⭐)

### `ci-doctor` — 16 repos

CI failure diagnosis via `workflow_run`. Copied across repos:

- [`devantler-tech/ksail/ci-doctor`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/ci-doctor.md) (130 ⭐)
- [`tosin2013/mcp-adr-analysis-server/ci-doctor`](https://github.com/tosin2013/mcp-adr-analysis-server/blob/main/.github/workflows/ci-doctor.md) (19 ⭐)
- [`sayinmehmet47/kitapKurdu/ci-doctor`](https://github.com/sayinmehmet47/kitapKurdu/blob/main/.github/workflows/ci-doctor.md) (17 ⭐)
- [`ianlintner/rust-oauth2-server/ci-doctor`](https://github.com/ianlintner/rust-oauth2-server/blob/main/.github/workflows/ci-doctor.md) (3 ⭐)

### `weekly-research` — 17 repos

Weekly research reports. Consistent naming across repos:

- [`github/gh-aw/weekly-issue-summary`](https://github.com/github/gh-aw/blob/main/.github/workflows/weekly-issue-summary.md) (3,356 ⭐)
- [`devantler-tech/ksail/weekly-research`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/weekly-research.md) (130 ⭐)
- [`lablup/backend.ai-webui/weekly-team-status`](https://github.com/lablup/backend.ai-webui/blob/main/.github/workflows/weekly-team-status.md) (125 ⭐)

## Pattern 2: Multi-Workflow Repos (Shared Context)

Some repos run many workflows that share context by being co-located.

### `github/gh-aw` — 120 workflows

The largest agentic workflow repo in the scan. Workflows share:
- The same repo context (codebase, issues, discussions)
- Shared Go packages (e.g., `imports: ["github.com/github/gh-aw/pkg/logger"]`)
- Common patterns (pre-steps, triggers, safety config)

**Specialized workflows in the suite:**
- [`github/gh-aw/firewall`](https://github.com/github/gh-aw/blob/main/.github/workflows/firewall.md) — Security firewall
- [`github/gh-aw/release`](https://github.com/github/gh-aw/blob/main/.github/workflows/release.md) — Release automation
- [`github/gh-aw/q`](https://github.com/github/gh-aw/blob/main/.github/workflows/q.md) — Q&A slash command
- [`github/gh-aw/tidy`](https://github.com/github/gh-aw/blob/main/.github/workflows/tidy.md) — Code cleanup

### `devantler-tech/ksail` — 14 workflows

A community repo with a full workflow suite:

- [`ksail/ci-doctor`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/ci-doctor.md) — CI diagnosis
- [`ksail/daily-perf-improver`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/daily-perf-improver.md) — Performance
- [`ksail/daily-code-simplifier`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/daily-code-simplifier.md) — Simplification
- [`ksail/unbloat-docs`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/unbloat-docs.md) — Doc cleanup
- [`ksail/weekly-research`](https://github.com/devantler-tech/ksail/blob/main/.github/workflows/weekly-research.md) — Research reports

### `Olino3/forge` — 11 workflows

A purpose-built workflow suite with explicit model selection per task:

- [`forge/forge-project-manager-agent`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-project-manager-agent.md) — `claude-opus-4.6` for planning
- [`forge/forge-dependency-update-sentinel`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-dependency-update-sentinel.md) — `gpt-5.1-codex-mini` for scanning
- [`forge/forge-release-notes-generator`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-release-notes-generator.md) — `claude-haiku-4.5` for prose
- [`forge/forge-feature-decomposer`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-feature-decomposer.md) — `claude-opus-4.6` for analysis

This demonstrates the **model-per-task** pattern: different models for different workflow types.

## Pattern 3: Imports (Explicit Shared Code)

The `imports` field allows workflows to reference shared code. Still rare:

- [`github/gh-aw/go-logger`](https://github.com/github/gh-aw/blob/main/.github/workflows/go-logger.md) — imports `"github.com/github/gh-aw/pkg/logger"` (3,356 ⭐)
- [`github/gh-aw-mcpg/go-logger`](https://github.com/github/gh-aw-mcpg/blob/main/.github/workflows/go-logger.md) — imports `"github.com/github/gh-aw-mcpg/internal/logger"` (45 ⭐)

**Current state:** Imports are used for Go package references within the same org. This pattern may expand as the ecosystem matures.

## Pattern 4: Naming Conventions as Reuse

Consistent naming across repos signals the same pattern. The top shared names:

| Name | Repos | Pattern |
|------|-------|---------|
| `daily-repo-status` | 57 | Daily health report |
| `issue-triage` | 18 | Issue classification |
| `weekly-research` | 17 | Weekly research digest |
| `ci-doctor` | 16 | CI failure diagnosis |
| `update-docs` | 14 | Documentation refresh |
| `daily-test-improver` | 13 | Test quality improvement |
| `code-simplifier` | 13 | Code complexity reduction |
| `upstream-monitor` | 11 | Upstream dependency watch |
| `typo-checker` | 10 | Typo detection |
| `daily-perf-improver` | 9 | Performance improvement |

## Rules

1. **Start by copying a proven pattern.** `daily-repo-status` exists in 57 repos — start there and customize.
2. **Use consistent naming.** If 18 repos call it `issue-triage`, call yours `issue-triage` too.
3. **Co-locate related workflows** in the same repo for shared context.
4. **Match models to tasks** in multi-workflow repos — cheap models for classification, expensive for planning (see Olino3/forge).
5. **Imports are emerging** but not yet widely used. Watch for this pattern to mature.
6. **A full workflow suite** covers: triage + daily improvement + weekly reports + CI diagnosis. See `devantler-tech/ksail` for a community example.
