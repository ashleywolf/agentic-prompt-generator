# Trigger Selection — When should my workflow run?

## Trigger Overview

| Trigger | Runs When | Frequency | Best For |
|---|---|---|---|
| `schedule:daily` | Cron (e.g., 9am UTC) | 1x/day | Improvement sweeps, daily reports |
| `schedule:weekly` | Cron (e.g., Monday 9am) | 1x/week | Recurring reports, health checks |
| `issues:[opened]` | New issue created | Event-driven | Triage, labeling, auto-response |
| `issues:[labeled]` | Label added to issue | Event-driven | Stage transitions, workflow routing |
| `pull_request` | PR opened/updated | Event-driven | Code review, doc sync |
| `workflow_run` | Another workflow finishes | Event-driven | CI failure diagnosis |
| `slash_command` | `/command` in comment | On-demand | Interactive tools, ad-hoc analysis |
| `workflow_dispatch` | Manual trigger in UI | On-demand | Migrations, one-off tasks |
| Multi-trigger | Multiple events → 1 workflow | Mixed | Lifecycle management |

---

## Pattern 1: schedule:daily

**When:** You want to sweep the codebase or repo daily for improvements.

### Production Examples

**code-simplifier** — daily code improvement sweep:
```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 9am UTC daily

steps:
  - agent:
      prompt: |
        Scan the codebase for opportunities to simplify complex functions.
        Focus on functions with cyclomatic complexity > 10.
        Create a PR with the simplifications.
```

**daily-qa** — daily test coverage check:
```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'  # 6am UTC, weekdays only

steps:
  - agent:
      prompt: |
        Review test coverage reports and identify untested critical paths.
        Create issues for the top 3 coverage gaps.
```

**Tips:**
- Use weekday-only crons (`1-5`) to avoid weekend noise
- Stagger times to avoid hitting API rate limits across multiple workflows
- Always set `stop-after` to auto-disable stale workflows

---

## Pattern 2: schedule:weekly

**When:** Recurring reports or health checks that aggregate a week's worth of data.

### Production Examples

**org-health** — weekly organization health report:
```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9am UTC

steps:
  - agent:
      prompt: |
        Generate a weekly org health report covering:
        - PR merge times (p50, p90)
        - Issue response times
        - CI success rates
        - Top contributors
```

**weekly-newsletter** — team activity summary:
```yaml
on:
  schedule:
    - cron: '0 14 * * 5'  # Friday 2pm UTC

steps:
  - run: python fetch_standup_data.py > /tmp/data.json
  - agent:
      prompt: |
        Write a concise weekly newsletter from /tmp/data.json.
        Highlight wins, blockers, and next week's priorities.
```

---

## Pattern 3: issues:[opened]

**When:** Every new issue should be processed immediately.

### Production Examples

**apollo** — [apollographql/apollo](https://github.com/apollographql):
```yaml
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        Triage this new issue:
        1. Check if it's a duplicate of an existing issue
        2. Classify as [bug, feature, question, docs]
        3. Add appropriate labels
        4. If it's a question, provide a helpful response
```

**rover** — [apollographql/rover](https://github.com/apollographql/rover):
```yaml
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        You are the Rover CLI triage bot.
        - Determine if this is a CLI bug, schema issue, or user error
        - Add labels: [cli-bug, schema, user-error, needs-repro]
        - If needs-repro, ask the user for reproduction steps
```

**Kong** — [Kong/kong](https://github.com/Kong/kong):
```yaml
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        Triage this Kong issue:
        - Identify affected component (proxy, admin-api, plugins, db)
        - Check version compatibility
        - Label with component and severity
```

---

## Pattern 4: schedule:daily Batch Processing

**When:** You want to process all recent issues in bulk rather than one-at-a-time.

### Production Example

**appwrite** — [appwrite/appwrite](https://github.com/appwrite/appwrite) processes all issues from the last 24h:
```yaml
on:
  schedule:
    - cron: '0 8 * * *'

steps:
  - run: |
      gh issue list --repo owner/repo --state open \
        --json number,title,body,labels,createdAt \
        --jq '[.[] | select(.createdAt > (now - 86400 | todate))]' \
        > /tmp/recent-issues.json

  - agent:
      prompt: |
        Process all issues in /tmp/recent-issues.json.
        For each issue, classify and label it.
        Skip issues that already have triage labels.
```

**When to use batch vs event-driven:**
- **Event-driven** (`issues:[opened]`): Immediate response matters, low volume (<20/day)
- **Batch** (`schedule:daily`): Consistency matters more than speed, high volume, or you need cross-issue analysis

---

## Pattern 5: slash_command

**When:** Users should be able to invoke the workflow on-demand via a comment.

### Production Examples

**/plan** — generate implementation plan:
```yaml
on:
  issue_comment:
    types: [created]
  # Filter for /plan command in the workflow

steps:
  - agent:
      prompt: |
        The user invoked /plan. Generate a detailed implementation plan
        for the issue or PR this comment is on.
```

**/nit** — nitpick code review:
```yaml
on:
  issue_comment:
    types: [created]

steps:
  - agent:
      prompt: |
        The user invoked /nit on this PR.
        Review the diff and leave inline comments about:
        - Naming conventions
        - Code style issues
        - Minor improvements
```

**/grumpy** — opinionated review:
```yaml
on:
  issue_comment:
    types: [created]

steps:
  - agent:
      prompt: |
        You are a grumpy senior engineer. Review this PR with
        brutal honesty but constructive feedback. Be funny but fair.
```

**/feedback** — solicit structured feedback:
```yaml
on:
  issue_comment:
    types: [created]

steps:
  - agent:
      prompt: |
        The user wants feedback. Analyze the issue/PR and provide
        structured feedback with pros, cons, and suggestions.
```

---

## Pattern 6: pull_request

**When:** PRs need automated review, doc sync, or performance checks.

### Production Examples

**doc-sync** — keep docs in sync with code:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - 'src/**'
      - 'docs/**'

steps:
  - agent:
      prompt: |
        Check if the code changes in this PR require documentation updates.
        If docs are outdated, suggest the specific changes needed.
```

**rust-performance** — performance regression detection:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    paths:
      - '**/*.rs'

steps:
  - agent:
      prompt: |
        Analyze the Rust code changes for potential performance regressions:
        - Unnecessary allocations
        - Missing `#[inline]` on hot paths
        - Lock contention issues
```

**Tip:** Use `paths:` filters to avoid running on irrelevant PRs.

---

## Pattern 7: workflow_run

**When:** React to another workflow's completion (typically CI failures).

### Production Examples

**ci-doctor** — diagnose CI failures:
```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    # Only trigger on failure — filter in the workflow logic

steps:
  - agent:
      prompt: |
        The CI workflow failed. Investigate:
        1. Download and read the workflow logs
        2. Identify the root cause
        3. Comment on the PR with the diagnosis and suggested fix
```

**workflow-doctor** — [JanDeDobbeleer/oh-my-posh](https://github.com/JanDeDobbeleer/oh-my-posh):
```yaml
on:
  workflow_run:
    workflows: ["Build", "Release"]
    types: [completed]

steps:
  - agent:
      model: claude-sonnet-4.5
      prompt: |
        A workflow has completed. If it failed:
        1. Analyze the failure logs
        2. Check if this is a known flaky test
        3. If new failure, investigate the triggering commit
        4. Post a diagnosis comment on the associated PR
```

---

## Pattern 8: issues:[labeled]

**When:** A label change should trigger the next stage of a workflow.

### Production Example

**forge-feature-decomposer** — [Olino3/forge](https://github.com/Olino3/forge):
```yaml
on:
  issues:
    types: [labeled]
    # Filter for label: "needs-decomposition"

steps:
  - agent:
      model: claude-opus-4.6
      prompt: |
        This issue has been labeled "needs-decomposition".
        Break it down into sub-issues with:
        - Clear acceptance criteria
        - Dependency graph
        - Complexity estimates
```

**Use case:** Build stage-gate workflows where human labels trigger automated next steps.

---

## Pattern 9: workflow_dispatch

**When:** Manual trigger for one-off tasks like migrations, upgrades, or doc generation.

### Production Examples

**upgrade-pylib** — upgrade a Python library across repos:
```yaml
on:
  workflow_dispatch:
    inputs:
      library:
        description: 'Library to upgrade (e.g., requests)'
        required: true
      version:
        description: 'Target version'
        required: true

steps:
  - agent:
      prompt: |
        Upgrade ${{ inputs.library }} to version ${{ inputs.version }}.
        1. Update requirements.txt / pyproject.toml
        2. Run tests
        3. Create a PR with the changes
```

**generate-error-docs** — regenerate error documentation:
```yaml
on:
  workflow_dispatch:

steps:
  - agent:
      prompt: |
        Scan the codebase for all error types and generate
        user-facing documentation for each one.
        Update docs/errors.md with the results.
```

---

## Pattern 10: Multi-trigger Routing

**When:** One workflow handles multiple lifecycle stages based on the trigger.

### Production Example

**forge-milestone-lifecycle** — [Olino3/forge](https://github.com/Olino3/forge) — 1 workflow, 3 triggers, 3 stages:

```yaml
on:
  issues:
    types: [opened]      # Stage 1: Triage
  issues:
    types: [labeled]     # Stage 2: Decompose (when labeled "approved")
  schedule:
    - cron: '0 9 * * 1'  # Stage 3: Weekly review

steps:
  - agent:
      prompt: |
        Determine which stage to execute based on the trigger:

        ## Stage 1: Triage (issue opened)
        - Classify the issue
        - Suggest milestone assignment

        ## Stage 2: Decompose (issue labeled "approved")
        - Break into sub-tasks
        - Create linked issues

        ## Stage 3: Weekly Review (Monday schedule)
        - Review all milestone progress
        - Flag at-risk items
        - Generate status report
```

---

## stop-after Guidance

**Always set `stop-after` to auto-disable workflows that shouldn't run forever.**

| Workflow Type | Recommended stop-after |
|---|---|
| Experimental / testing | `+7d` |
| Campaign (limited run) | `+30d` or `+1mo` |
| Seasonal (quarterly) | `+90d` |
| Permanent (core triage) | Don't set (or `+1y` for safety) |

```yaml
stop-after: "+30d"  # Auto-disable after 30 days
```

**Why this matters:**
- Forgotten workflows waste compute and generate noise
- Schedule-triggered workflows especially — they run even when no one is watching
- `stop-after` is your safety net

---

## Quick Reference

```
Immediate response to new issues?     → issues:[opened]
Immediate response to PRs?            → pull_request
React to CI failures?                 → workflow_run
Daily improvement sweep?              → schedule:daily
Weekly report or health check?        → schedule:weekly
User-invoked tool?                    → slash_command
Label-driven stage gate?              → issues:[labeled]
One-off migration or upgrade?         → workflow_dispatch
Complex lifecycle with many stages?   → Multi-trigger routing
High-volume issue processing?         → schedule:daily batch
```
