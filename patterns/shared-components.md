# Shared Components — How do I reuse logic across workflows?

## The Problem

As your workflows grow, you'll notice duplication:
- Multiple workflows use the same model configuration
- Multiple workflows share reporting templates
- Multiple workflows need the same MCP server setup
- Multiple workflows across repos need the same base prompt

**The solution:** Extract shared logic into reusable modules and import them.

---

## Import Mechanisms

| Mechanism | Scope | Use Case |
|---|---|---|
| `imports: shared/*.md` | Same repo | Shared configs within a project |
| `source: owner/repo/file@sha` | Cross-repo | Shared base across an organization |

---

## Pattern 1: Shared Reporting Template

**When:** Multiple workflows produce reports with the same format.

### Production Example — github/gh-aw

```
repo/
├── .github/copilot/
│   ├── workflows/
│   │   ├── portfolio-analyst.yml
│   │   ├── weekly-summary.yml
│   │   └── cost-report.yml
│   └── shared/
│       └── reporting.md
```

**shared/reporting.md:**
```markdown
## Report Formatting Standards

All reports MUST follow these formatting rules:

### Structure
1. Executive summary (3 sentences max)
2. Key metrics table
3. Trends (compared to previous period)
4. Recommendations (actionable, specific)
5. Appendix (raw data, if needed)

### Metric Tables
Use this format:
| Metric | Current | Previous | Trend |
|--------|---------|----------|-------|
| {name} | {value} | {value}  | ↑/↓/→ |

### Trend Indicators
- ↑ Green: Improvement
- ↓ Red: Regression  
- → Gray: No significant change

### Tone
- Professional but not stuffy
- Data-driven — every claim backed by a number
- Concise — no filler paragraphs
```

**Workflow using the import:**
```yaml
# portfolio-analyst.yml
imports:
  - shared/reporting.md

steps:
  - agent:
      prompt: |
        Generate a portfolio analysis report.
        Follow the reporting standards from the shared guidelines.
        
        Focus on:
        - Top 5 workflows by cost
        - Failure rate trends
        - Optimization recommendations
```

**Why this works:**
- Change the reporting template once, all workflows update
- Consistent formatting across all reports
- New workflows automatically follow the standard

---

## Pattern 2: Shared Model Configuration

**When:** Multiple workflows should use the same model to ensure consistent behavior.

### Production Example — Olino3/forge

[Olino3/forge](https://github.com/Olino3/forge) uses a shared model config for classification tasks:

```
repo/
├── .github/copilot/
│   ├── workflows/
│   │   ├── forge-duplication-detector.yml
│   │   ├── forge-dependency-update-sentinel.yml
│   │   └── forge-issue-classifier.yml
│   └── shared/
│       └── model-codex-mini.md
```

**shared/model-codex-mini.md:**
```markdown
## Model Configuration

Use model: gpt-5.1-codex-mini for this workflow.

### Behavior Guidelines for Codex Mini
- Respond with structured output (JSON when possible)
- Keep responses concise — this model is optimized for speed
- Use classification labels, not free-form text
- If confidence is below 70%, output "uncertain" instead of guessing
```

**Workflow using the import:**
```yaml
# forge-duplication-detector.yml
imports:
  - shared/model-codex-mini.md

steps:
  - agent:
      model: gpt-5.1-codex-mini
      prompt: |
        Detect if this issue is a duplicate.
        Follow the model behavior guidelines.
        Output: { "is_duplicate": bool, "similar_issue": "#N or null", "confidence": 0.0-1.0 }
```

---

## Pattern 3: Shared Base Configuration (Best Example)

**When:** All workflows in a project share common identity, rules, and context.

### Production Example — Olino3/forge

[Olino3/forge](https://github.com/Olino3/forge) has the best import architecture — **4 workflows sharing 5 modules:**

```
repo/
├── .github/copilot/
│   ├── workflows/
│   │   ├── forge-feature-decomposer.yml
│   │   ├── forge-duplication-detector.yml
│   │   ├── forge-dependency-update-sentinel.yml
│   │   └── forge-milestone-lifecycle.yml
│   └── shared/
│       ├── forge-base.md            # Core identity & rules
│       ├── model-codex-mini.md      # Fast model config
│       ├── model-opus.md            # Reasoning model config
│       ├── labels.md                # Allowed label taxonomy
│       └── repo-context.md          # Repository structure guide
```

**shared/forge-base.md:**
```markdown
## Forge — Base Configuration

You are Forge, an intelligent project management agent for this repository.

### Identity
- Name: Forge
- Role: Project management automation
- Repository: Olino3/forge

### Core Rules
1. Never modify code directly — create issues and PRs for changes
2. Always check for existing issues before creating new ones
3. Use the label taxonomy from shared/labels.md
4. Be concise — developers have limited attention
5. When uncertain, ask via a comment rather than guessing

### Repository Structure
- `src/` — Main application code (TypeScript)
- `tests/` — Test suites
- `docs/` — Documentation
- `.github/` — CI/CD and workflow configs

### Communication Style
- Professional but friendly
- Use bullet points, not paragraphs
- Include issue/PR links when referencing related work
- Sign off with "— Forge 🔨"
```

**shared/labels.md:**
```markdown
## Label Taxonomy

### Type Labels (mutually exclusive)
- `bug` — Something is broken
- `feature` — New functionality request
- `chore` — Maintenance, refactoring, deps
- `docs` — Documentation changes

### Priority Labels (mutually exclusive)
- `priority:critical` — Blocks release
- `priority:high` — Should be in next sprint
- `priority:medium` — Should be in next milestone
- `priority:low` — Nice to have

### Status Labels
- `needs-triage` — Not yet classified
- `needs-repro` — Needs reproduction steps
- `ready` — Ready for development
- `in-progress` — Being worked on
- `blocked` — Blocked by dependency
```

**Workflow using multiple imports:**
```yaml
# forge-feature-decomposer.yml
imports:
  - shared/forge-base.md
  - shared/model-opus.md
  - shared/labels.md

steps:
  - agent:
      model: claude-opus-4.6
      prompt: |
        Decompose this feature request into sub-issues.
        Follow the Forge base rules and use the label taxonomy.
        
        For each sub-issue:
        1. Title (concise, imperative mood)
        2. Description (what and why)
        3. Labels from the taxonomy
        4. Dependencies (which sub-issues must complete first)
        5. Acceptance criteria (testable)
```

**Why Forge's architecture is exemplary:**
- `forge-base.md` — Shared identity means consistent behavior across all 4 workflows
- `model-*.md` — Model selection is centralized, easy to upgrade
- `labels.md` — Single source of truth for label taxonomy
- Any change to a shared file updates all workflows that import it

---

## Pattern 4: Shared MCP Server Configuration

**When:** Multiple workflows need access to the same external services via MCP.

### Production Example — Datadog Integration

```
repo/
├── .github/copilot/
│   ├── workflows/
│   │   ├── slo-report.yml
│   │   ├── incident-analysis.yml
│   │   └── capacity-planning.yml
│   └── shared/
│       └── mcp/
│           └── datadog.md
```

**shared/mcp/datadog.md:**
```markdown
## Datadog MCP Server Configuration

### Available Tools
- `datadog.metrics.query` — Query metric timeseries
- `datadog.monitors.list` — List active monitors
- `datadog.monitors.get` — Get monitor details
- `datadog.events.list` — List events (deployments, alerts)

### Usage Guidelines
- Always specify a time range (default: last 7 days)
- Use `avg` aggregation unless specifically asked for `max` or `sum`
- Rate limit: max 10 queries per workflow run
- Metric names follow pattern: `service.{name}.{metric}`

### Common Metrics
| Metric | Description | Unit |
|--------|-------------|------|
| `service.api.latency.p99` | API p99 latency | ms |
| `service.api.error_rate` | Error rate | % |
| `service.api.request_count` | Request volume | count/s |
| `service.db.connection_pool` | DB pool utilization | % |
```

---

## Pattern 5: Cross-repo Inheritance (source)

**When:** Multiple repos across an organization need to share the same base workflow.

### How It Works

Instead of `imports` (same repo), use `source` to reference a file in another repository:

```yaml
source: owner/shared-workflows/base-triage.md@main
```

The `@sha` or `@branch` pins the version, so upstream changes don't break your workflow unexpectedly.

### Production Example — appwrite

[appwrite/appwrite](https://github.com/appwrite/appwrite) — shared triage base across multiple repos:

```yaml
# In appwrite/appwrite repo
source: appwrite/workflow-templates/triage-base.md@v1.2.0

steps:
  - agent:
      prompt: |
        Triage this issue using the base triage rules.
        Additional rules for the main appwrite repo:
        - Check if the issue mentions a specific SDK
        - If SDK-specific, transfer to the SDK repo
```

### Production Example — Kong

[Kong/kong](https://github.com/Kong/kong) — shared across Kong ecosystem:

```yaml
# In Kong/kong repo
source: Kong/workflow-templates/oss-triage.md@main

steps:
  - agent:
      prompt: |
        Triage this Kong issue using the OSS triage guidelines.
        Additional context: Kong-specific component labels.
```

### Production Example — orca

Cross-repo inheritance for a multi-repo project:

```yaml
# In each microservice repo
source: org/platform-workflows/service-review.md@sha256abc

steps:
  - agent:
      prompt: |
        Review this PR using the platform review standards.
        This service-specific addition: check for API contract compliance.
```

### Version Pinning Strategies

| Strategy | Syntax | Use Case |
|---|---|---|
| Branch (latest) | `@main` | Templates that should always be current |
| Tag (versioned) | `@v1.2.0` | Production workflows that need stability |
| SHA (exact) | `@abc123` | Maximum reproducibility |

**Recommendation:** Use `@tag` for production, `@main` for development/testing.

---

## Architecture Patterns

### Small Project (1-2 workflows)

No shared components needed. Keep it simple.

```
.github/copilot/
├── workflows/
│   ├── triage.yml
│   └── review.yml
```

### Medium Project (3-5 workflows)

Extract common configs into shared files.

```
.github/copilot/
├── workflows/
│   ├── triage.yml
│   ├── review.yml
│   ├── report.yml
│   └── improvement.yml
└── shared/
    ├── base.md
    ├── labels.md
    └── reporting.md
```

### Large Project / Organization (5+ workflows across repos)

Use cross-repo inheritance + per-repo shared configs.

```
# Central template repo
org/workflow-templates/
├── triage-base.md
├── review-base.md
├── reporting-base.md
└── safety-defaults.md

# Each project repo
project-repo/.github/copilot/
├── workflows/
│   ├── triage.yml        # source: org/workflow-templates/triage-base.md@v1
│   └── review.yml        # source: org/workflow-templates/review-base.md@v1
└── shared/
    ├── project-context.md  # Project-specific overrides
    └── labels.md           # Project-specific labels
```

---

## Common Gotchas

1. **Don't over-extract.** If only one workflow uses a piece of config, leave it inline. Extract when 2+ workflows share it.
2. **Pin cross-repo sources.** Using `@main` means upstream changes can break your workflow without warning. Use tags for production.
3. **Keep shared files focused.** One file = one concern. Don't create a "shared/everything.md" monolith.
4. **Document import dependencies.** When a workflow imports 3 files, it's not obvious what each one provides. Add a comment.
5. **Test after shared file changes.** Changing `shared/labels.md` affects every workflow that imports it. Test them all.
6. **Shared ≠ required.** Not every workflow needs every shared file. Import only what's needed.
