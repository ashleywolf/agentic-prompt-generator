# Model Selection

> **"Which model should I use?"**

## The Numbers

From **679 workflows** across **269 repos**:

| Model | Workflows | Usage |
|-------|-----------|-------|
| Default (no explicit model) | 631 | 93% |
| `gpt-5.1-codex-mini` | 17 | 2.5% |
| `claude-opus-4.6` / `claude-opus-4-6` | 11 | 1.6% |
| `claude-haiku-4.5` | 3 | 0.4% |
| `gpt-5.2` | 2 | 0.3% |
| `gpt-5` | 2 | 0.3% |
| `claude-sonnet-4` / `4.5` / `4.6` | 4 | 0.6% |
| Other (`gemini`, `gpt-4o`, `gpt-4.1`) | 4 | 0.6% |

**93% of workflows use the platform default.** Explicit model selection is the exception, not the rule.

## Decision Table

| Task Type | Recommended Model | Why | Real Example |
|-----------|-------------------|-----|--------------|
| Classification / triage | `gpt-5.1-codex-mini` | Fast, cheap, good enough for labels | [`Olino3/forge/forge-stale-gardener`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-stale-gardener.md) |
| Scheduled batch work | `gpt-5.1-codex-mini` | High volume, cost matters | [`drehelis/gcp-emulator-ui/check-emulator-updates`](https://github.com/drehelis/gcp-emulator-ui/blob/main/.github/workflows/check-emulator-updates.md) |
| Code review / investigation | Default or `claude-sonnet` | Balanced reasoning + speed | [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) |
| PR analysis | `claude-sonnet-4.5` | Strong code understanding | [`HemSoft/hs-buddy/pr-analyzer-a`](https://github.com/HemSoft/hs-buddy/blob/main/.github/workflows/pr-analyzer-a.md) |
| Complex planning / architecture | `claude-opus-4.6` | Deep reasoning needed | [`phpstan/phpstan/generate-error-docs`](https://github.com/phpstan/phpstan/blob/main/.github/workflows/generate-error-docs.md) |
| Cross-repo sync / deep analysis | `claude-opus-4.6` | Multi-step, high stakes | [`npgsql/efcore.pg/sync-to-latest-ef`](https://github.com/npgsql/efcore.pg/blob/main/.github/workflows/sync-to-latest-ef.md) |
| Doc generation | `claude-haiku-4.5` | Good prose, low cost | [`Olino3/forge/forge-doc-maintainer`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-doc-maintainer.md) |
| Everything else | Default | Let the platform optimize | 93% of all workflows |

## Real Examples by Model

### `gpt-5.1-codex-mini` — The Workhorse (17 workflows)

Used for high-volume, classification, and batch tasks where cost matters:

- [`drehelis/gcp-emulator-ui/check-emulator-updates`](https://github.com/drehelis/gcp-emulator-ui/blob/main/.github/workflows/check-emulator-updates.md) — Check upstream GCP emulator changes (35 ⭐)
- [`Olino3/forge/forge-dependency-update-sentinel`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-dependency-update-sentinel.md) — Dependency scanning
- [`Olino3/forge/forge-stale-gardener`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-stale-gardener.md) — Stale issue cleanup
- [`TJKlein/AgentKernel/issue-monster`](https://github.com/TJKlein/AgentKernel/blob/main/.github/workflows/issue-monster.md) — Issue labeling at scale (5 ⭐)
- [`Canepro/pipelinehealer/ci-doctor`](https://github.com/Canepro/pipelinehealer/blob/main/.github/workflows/ci-doctor.md) — CI failure triage (1 ⭐)

### `claude-opus-4.6` — The Thinker (11 workflows)

Used when deep reasoning, multi-step planning, or high-stakes decisions are needed:

- [`phpstan/phpstan/generate-error-docs`](https://github.com/phpstan/phpstan/blob/main/.github/workflows/generate-error-docs.md) — Generate comprehensive error documentation (13,829 ⭐)
- [`npgsql/efcore.pg/sync-to-latest-ef`](https://github.com/npgsql/efcore.pg/blob/main/.github/workflows/sync-to-latest-ef.md) — Sync codebase to upstream EF Core changes (1,801 ⭐)
- [`elastic/opentelemetry-collector-components/pr-review`](https://github.com/elastic/opentelemetry-collector-components/blob/main/.github/workflows/pr-review.md) — Deep PR review (16 ⭐)
- [`Hack23/riksdagsmonitor/news-evening-analysis`](https://github.com/Hack23/riksdagsmonitor/blob/main/.github/workflows/news-evening-analysis.md) — Parliamentary news analysis with pre-steps (2 ⭐)
- [`Olino3/forge/forge-feature-decomposer`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-feature-decomposer.md) — Break features into tasks
- [`Olino3/forge/forge-project-manager-agent`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-project-manager-agent.md) — Project planning

### `claude-sonnet-4.5` — The Investigator (4 workflows)

Balanced reasoning for code analysis:

- [`JanDeDobbeleer/oh-my-posh/workflow-doctor`](https://github.com/JanDeDobbeleer/oh-my-posh/blob/main/.github/workflows/workflow-doctor.md) — Diagnoses CI failures after `workflow_run` (21,566 ⭐)

### `claude-haiku-4.5` — The Documenter (3 workflows)

Fast, good prose output, low cost:

- [`Olino3/forge/forge-release-notes-generator`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-release-notes-generator.md) — Generate release notes
- [`Olino3/forge/forge-doc-maintainer`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-doc-maintainer.md) — Keep docs updated
- [`Olino3/forge/forge-health-dashboard`](https://github.com/Olino3/forge/blob/main/.github/workflows/forge-health-dashboard.md) — Health summary reports

### Multi-Model Comparison

[`HemSoft/hs-buddy`](https://github.com/HemSoft/hs-buddy) runs the same PR analysis with three different models:
- `pr-analyzer-a` → `claude-sonnet-4-5`
- `pr-analyzer-b` → `gemini-2-pro`
- `pr-analyzer-c` → `gpt-4o`

This is a useful pattern for evaluating model performance on your specific task.

## Rules

1. **Start with the default.** 93% of workflows don't specify a model. Only override when you have a reason.
2. **Use `codex-mini` for classification tasks** — labeling, triage, simple checks. It's fast and cheap.
3. **Use `opus` for planning and architecture** — feature decomposition, cross-repo sync, doc generation from complex code.
4. **Use `haiku` for prose-heavy output** — release notes, docs, reports. Good quality at low cost.
5. **Use `sonnet` for code investigation** — CI debugging, PR review, code analysis. Balanced reasoning + speed.
6. **Match cost to stakes** — a daily triage workflow runs 365×/year; use a cheap model. A quarterly architecture review runs 4×/year; use the best.
