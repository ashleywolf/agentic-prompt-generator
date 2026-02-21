# Output Selection — Where should results go?

## The Key Insight

> **`create-discussion` with `close-older: true` is THE pattern for recurring reports.**

It gives you a clean, auto-archiving feed of reports without issue/PR clutter.

---

## Output Overview

| Output | Best For | Recurring? | Key Options |
|---|---|---|---|
| `create-discussion` | Reports, summaries, dashboards | ✅ Yes | `close-older`, `expires`, `category` |
| `create-issue` | Actionable items, bugs, tasks | ⚠️ Sometimes | `title-prefix`, `labels`, `expires` |
| `add-comment` | Feedback on existing items | ❌ No | `target`, `hide-older-comments` |
| `create-pull-request` | Code changes | ❌ No | `draft`, `if-no-changes` |
| `create-pull-request-review-comment` | Inline code review | ❌ No | `max` |
| `add-labels` | Classification | ❌ No | `allowed` |
| `dispatch-workflow` | Pipeline chaining | ❌ No | `workflow`, `inputs` |
| `upload-asset` | Charts, images, artifacts | ❌ No | `path` |
| noop (Job Summary) | Logs, debugging | ❌ No | — |

---

## Pattern 1: create-discussion

**When:** Recurring reports, weekly summaries, dashboards, SLO reviews.

**This is the single most important output pattern.** If your workflow generates a report on a schedule, use discussions.

### Why Discussions > Issues for Reports
- Issues clutter your backlog and confuse triage
- Discussions have categories (organize by type)
- `close-older: true` auto-archives previous reports
- Team members can reply/react without affecting issue counts

### Production Example — Weekly Report

```yaml
outputs:
  - type: create-discussion
    config:
      category: "Reports"
      title-prefix: "Weekly Health Report"
      close-older: true    # Auto-close last week's report
      expires: "14d"       # Auto-lock after 14 days
```

### Production Example — Daily SLO Dashboard

```yaml
outputs:
  - type: create-discussion
    config:
      category: "SLO"
      title-prefix: "Daily SLO Report"
      close-older: true
      expires: "7d"
```

### close-older Behavior

When `close-older: true` is set:
1. The workflow creates a new discussion
2. It finds any previous discussion with the same `title-prefix`
3. It closes (locks) the older discussion
4. Result: You always have exactly **one active report** per category

```
Week 1: "Weekly Health Report — Jan 6" (active)
Week 2: "Weekly Health Report — Jan 13" (active) → "Weekly Health Report — Jan 6" (closed)
Week 3: "Weekly Health Report — Jan 20" (active) → "Weekly Health Report — Jan 13" (closed)
```

---

## Pattern 2: create-issue

**When:** The agent identifies something that needs human action — a bug, a task, a follow-up.

### Production Example — Actionable Findings

```yaml
outputs:
  - type: create-issue
    config:
      title-prefix: "[auto] "
      labels: ["automated", "needs-review"]
      expires: "30d"       # Auto-close if not acted on in 30 days
```

### Production Example — Daily Improvement Issues

```yaml
outputs:
  - type: create-issue
    config:
      title-prefix: "[daily-qa] "
      labels: ["test-coverage", "automated"]
      max: 3               # Don't create more than 3 issues per run
      expires: "14d"
```

**Gotchas:**
- Always use `title-prefix` so humans can filter automated issues
- Always set `max` to prevent runaway issue creation
- Always set `expires` so stale issues auto-close
- Use `labels` so automated issues are easy to find/filter

---

## Pattern 3: add-comment

**When:** Responding to an issue or PR that triggered the workflow.

### Production Example — Triage Response

```yaml
outputs:
  - type: add-comment
    config:
      target: triggering        # Comment on the issue/PR that triggered this
      hide-older-comments: true  # Collapse previous bot comments
```

### Production Example — CI Failure Diagnosis

```yaml
outputs:
  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true
```

### hide-older-comments Behavior

When `hide-older-comments: true`:
- Previous comments from this workflow are minimized (collapsed)
- Only the latest comment is fully visible
- Prevents long threads of bot comments from cluttering the conversation

**Always use `hide-older-comments: true`** for workflows that may comment multiple times on the same item (e.g., CI doctor commenting on each push).

---

## Pattern 4: create-pull-request

**When:** The agent made code changes that need review.

### Production Example — Daily Improvement PR

```yaml
outputs:
  - type: create-pull-request
    config:
      draft: true              # Always start as draft
      if-no-changes: ignore    # Don't create empty PRs
      labels: ["automated"]
      title-prefix: "[auto] "
```

### Production Example — Doc Sync PR

```yaml
outputs:
  - type: create-pull-request
    config:
      draft: true
      if-no-changes: ignore
      base: main
      labels: ["docs", "automated"]
```

**Critical settings:**
- **`draft: true`** — Always. Automated PRs should never auto-merge without review.
- **`if-no-changes: ignore`** — Prevents empty PRs when the agent finds nothing to change.

---

## Pattern 5: create-pull-request-review-comment

**When:** The agent should leave inline review comments on specific code lines.

### Production Example — Nitpick Reviewer

```yaml
outputs:
  - type: create-pull-request-review-comment
    config:
      max: 5                   # Don't overwhelm — 5-10 comments max
```

### Production Example — Performance Review

```yaml
outputs:
  - type: create-pull-request-review-comment
    config:
      max: 10
```

**Guidelines:**
- **Set `max: 5` to `max: 10`** — More than 10 inline comments is overwhelming
- Fewer, higher-quality comments beat many trivial ones
- The agent should prioritize comments by severity

---

## Pattern 6: add-labels

**When:** The agent's primary job is to classify/categorize.

### Production Example — Issue Triage Labels

```yaml
outputs:
  - type: add-labels
    config:
      allowed:
        - bug
        - feature-request
        - question
        - documentation
        - good-first-issue
        - needs-repro
```

**Critical: Always use `allowed` list.** Without it, the agent may invent labels that don't exist in your repo, creating label pollution.

### Production Example — Priority Labels

```yaml
outputs:
  - type: add-labels
    config:
      allowed:
        - priority:critical
        - priority:high
        - priority:medium
        - priority:low
```

---

## Pattern 7: dispatch-workflow

**When:** Chaining workflows together — the output of one triggers the next.

### Production Example — Content Pipeline

```yaml
# Workflow 1: Blog Drafter
outputs:
  - type: dispatch-workflow
    config:
      workflow: blog-linker.yml
      inputs:
        draft_id: "${{ steps.draft.outputs.id }}"
        title: "${{ steps.draft.outputs.title }}"
```

```yaml
# Workflow 2: Blog Linker (triggered by dispatch)
on:
  workflow_dispatch:
    inputs:
      draft_id:
        required: true
      title:
        required: true

steps:
  - agent:
      prompt: |
        Add internal links and SEO metadata to draft ${{ inputs.draft_id }}.
```

**Use case:** Build multi-stage pipelines where each stage is a separate workflow.

---

## Pattern 8: upload-asset

**When:** The agent generates charts, images, or binary artifacts.

### Production Example — SLO Chart

```yaml
steps:
  - run: python generate_chart.py --output /tmp/slo-chart.png

outputs:
  - type: upload-asset
    config:
      path: /tmp/slo-chart.png
```

**Tip:** Generate charts in a pre-step, then upload as an asset. The agent can reference the asset URL in discussions or comments.

---

## Pattern 9: noop (Job Summary Only)

**When:** You just want to log results without creating any GitHub artifacts.

### Production Example — Dry Run / Debug

```yaml
outputs: []
# Results appear only in the Job Summary (Actions tab)
```

**When to use:**
- Testing a new workflow before enabling outputs
- Workflows where the value is in the agent's analysis, not an artifact
- Internal debugging workflows

---

## Combining Outputs

Many production workflows use **multiple outputs**:

### Example: Triage + Label + Comment

```yaml
outputs:
  - type: add-labels
    config:
      allowed: [bug, feature, question, duplicate]

  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true
```

### Example: Report + Artifact

```yaml
outputs:
  - type: create-discussion
    config:
      category: "Reports"
      title-prefix: "Weekly SLO"
      close-older: true
      expires: "14d"

  - type: upload-asset
    config:
      path: /tmp/slo-chart.png
```

---

## Quick Reference

```
Recurring report?                    → create-discussion (close-older: true)
Actionable finding?                  → create-issue (max + expires)
Responding to a trigger?             → add-comment (target: triggering)
Made code changes?                   → create-pull-request (draft: true)
Inline code feedback?                → create-pull-request-review-comment (max: 5-10)
Classifying/labeling?                → add-labels (allowed: [...])
Chaining to next workflow?           → dispatch-workflow
Generated an image/chart?            → upload-asset
Just logging/debugging?              → noop (Job Summary)
```

---

## Common Gotchas

1. **Issues ≠ Reports.** Don't use `create-issue` for recurring reports — they'll clutter your backlog. Use `create-discussion`.
2. **Always set `max` on create-issue.** Without it, a confused agent can create 50 issues in one run.
3. **Always set `expires`.** Stale automated content should self-clean.
4. **Always use `draft: true` for PRs.** Never let automated code auto-merge.
5. **Always use `allowed` for labels.** Agents will invent creative labels if you let them.
6. **Always use `hide-older-comments: true`** for workflows that comment repeatedly.
