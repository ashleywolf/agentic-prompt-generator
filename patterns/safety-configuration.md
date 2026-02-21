# Safety Configuration — How do I lock this down?

## Why Safety Configuration Matters

Agentic workflows run autonomously. Without guardrails:
- A triage bot creates 200 issues in one run
- A reviewer leaves 50 inline comments on a PR
- A report workflow creates discussions that pile up forever
- An agent with network access hits external APIs you didn't intend

**Every production workflow should have explicit safety limits.**

---

## Quick Reference Table

| Setting | What It Controls | Common Values |
|---|---|---|
| `max` | Maximum outputs per run | 1 (reports), 3-5 (triage), 10 (reviews), 100 (campaigns) |
| `expires` | Auto-cleanup of created artifacts | 1d, 7d, 14d, 30d |
| `close-older` | Auto-close previous instances | true/false |
| `target` | Where comments go | `triggering`, issue number, PR number |
| `allowed` | Whitelist of allowed values | Label lists, categories |
| `network.allowed` | Allowed network destinations | Domain allowlist |
| `stop-after` | Auto-disable the workflow | +7d, +30d, +1mo, +90d |
| `rate-limit` | Max runs per time window | 5/hour, 20/day |
| `roles` | Who can trigger | maintainer, collaborator, member |
| `permissions` | Repository permissions | read, write, admin |
| `hide-older-comments` | Collapse previous bot comments | true/false |
| `draft` | PR starts as draft | true/false |
| `if-no-changes` | What to do when no changes | ignore, fail |
| `lock-for-agent` | Prevent concurrent agent edits | true/false |
| `strict` | Enforce all safety rules strictly | true/false |

---

## Max Limits

Control how many artifacts the agent creates per run.

### Guidelines by Workflow Type

| Workflow Type | Recommended Max | Why |
|---|---|---|
| Recurring reports | `max: 1` | One report per run |
| Issue triage (per trigger) | `max: 1` | One response per issue |
| Batch triage (daily) | `max: 3-5` | Limit daily noise |
| Code review comments | `max: 5-10` | Avoid overwhelming PRs |
| Improvement PRs | `max: 1-3` | Each PR needs human review |
| Campaign/migration | `max: 50-100` | High volume, bounded |

### Examples

```yaml
# Report — exactly one discussion per run
outputs:
  - type: create-discussion
    config:
      max: 1

# Triage — up to 3 issues per daily run
outputs:
  - type: create-issue
    config:
      max: 3

# Code review — up to 5 inline comments
outputs:
  - type: create-pull-request-review-comment
    config:
      max: 5

# Migration campaign — up to 100 PRs total
outputs:
  - type: create-pull-request
    config:
      max: 100
```

**Without `max`, a confused agent can create unlimited artifacts.** Always set it.

---

## Expiration (expires)

Auto-cleanup artifacts after a time period.

### Guidelines

| Artifact Type | Recommended Expires | Why |
|---|---|---|
| Daily reports | `1d` or `7d` | Yesterday's report is stale |
| Weekly reports | `14d` | Keep 2 weeks of history |
| Triage issues | `30d` | If not acted on in 30 days, auto-close |
| Campaign PRs | `14d` | If not merged in 2 weeks, probably stale |
| Alert discussions | `7d` | Alerts lose relevance quickly |

### Examples

```yaml
# Daily report — expires in 7 days
outputs:
  - type: create-discussion
    config:
      expires: "7d"
      close-older: true

# Triage issue — expires in 30 days
outputs:
  - type: create-issue
    config:
      expires: "30d"
      labels: ["automated"]

# Alert — expires in 1 day
outputs:
  - type: create-discussion
    config:
      expires: "1d"
```

---

## close-older

Auto-close previous instances of recurring outputs.

```yaml
outputs:
  - type: create-discussion
    config:
      title-prefix: "Weekly Report"
      close-older: true     # Closes last week's report when this week's is created
```

**Always use `close-older: true` for recurring reports.** Without it, you'll accumulate dozens of open discussions.

---

## Target and hide-older-comments

Control where comments go and how they behave.

```yaml
outputs:
  - type: add-comment
    config:
      target: triggering          # Comment on the item that triggered the workflow
      hide-older-comments: true   # Collapse previous comments from this workflow
```

### target Options

| Value | Where Comment Goes |
|---|---|
| `triggering` | The issue/PR that triggered the workflow |
| `{issue_number}` | A specific issue |
| `{pr_number}` | A specific PR |

**Always use `hide-older-comments: true`** for workflows that may comment multiple times. Without it, the conversation gets buried under bot comments.

---

## Allowed Labels Whitelist

Prevent the agent from inventing labels.

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
        - priority:critical
        - priority:high
        - priority:medium
        - priority:low
```

**Without `allowed`, agents will create labels like "possibly-related-to-authentication" or "interesting-edge-case".** Always whitelist.

---

## Network Restrictions

Control what external services the agent can access.

```yaml
safety:
  network:
    allowed:
      - "api.github.com"
      - "registry.npmjs.org"
      - "pypi.org"
```

### Common Allowlists by Workflow Type

| Workflow Type | Allowed Domains |
|---|---|
| GitHub-only | `api.github.com` |
| Node.js project | `api.github.com`, `registry.npmjs.org` |
| Python project | `api.github.com`, `pypi.org` |
| Cloud monitoring | `api.github.com`, `management.azure.com`, `api.datadoghq.com` |
| Fully restricted | `[]` (empty — no network access) |

**Default to restrictive.** Only add domains the agent actually needs.

---

## stop-after

Auto-disable the workflow after a time period. Your safety net against forgotten workflows.

```yaml
safety:
  stop-after: "+30d"    # Disable after 30 days
```

### Recommended Values

| Workflow Lifespan | stop-after |
|---|---|
| Testing / experimental | `+7d` |
| Campaign (e.g., migrate all repos) | `+30d` or `+1mo` |
| Quarterly review | `+90d` |
| Permanent (core triage) | Don't set, or `+1y` for safety |

**Always set `stop-after` for scheduled workflows.** A weekly report that runs for 3 years after everyone forgot about it wastes resources and creates noise.

---

## Rate Limiting

Prevent runaway execution.

```yaml
safety:
  rate-limit:
    max-runs: 5
    per: hour
```

### Common Configurations

| Trigger Type | Rate Limit |
|---|---|
| `issues:[opened]` (high-traffic repo) | `20/hour` |
| `schedule:daily` | Not needed (already limited by cron) |
| `slash_command` | `10/hour` per user |
| `pull_request` | `10/hour` |

---

## Roles and Permissions

Control who can trigger and what the agent can do.

### Roles (Who Can Trigger)

```yaml
safety:
  roles:
    - maintainer
    - collaborator
```

| Role | Who |
|---|---|
| `maintainer` | Repo maintainers only |
| `collaborator` | Anyone with write access |
| `member` | Organization members |
| `contributor` | Anyone who has contributed |

**For slash commands, always restrict roles.** Otherwise, anyone who can comment can trigger your workflow.

### Permissions (What the Agent Can Do)

```yaml
safety:
  permissions:
    contents: read          # Can read code, not write
    issues: write           # Can create/modify issues
    pull-requests: write    # Can create/modify PRs
    discussions: write      # Can create discussions
```

**Principle of least privilege.** Only grant the permissions the workflow actually needs.

---

## lock-for-agent

Prevent concurrent agent runs from conflicting.

```yaml
safety:
  lock-for-agent: true
```

**When to use:**
- Workflows that modify the same files
- Workflows that create PRs (avoid duplicate PRs)
- Batch processing workflows (avoid processing the same item twice)

---

## strict Mode

Enforce all safety rules without exceptions.

```yaml
safety:
  strict: true
```

When `strict: true`:
- Agent cannot exceed `max` limits even if instructed to
- Agent cannot access non-allowed network destinations
- Agent cannot create non-allowed labels
- All safety violations cause the run to fail immediately

---

## Production Safety Profiles

### Minimal (Testing)

```yaml
safety:
  stop-after: "+7d"

outputs:
  - type: add-comment
    config:
      target: triggering
      max: 1
```

### Standard (Triage)

```yaml
safety:
  stop-after: "+90d"
  roles: [maintainer, collaborator]
  rate-limit:
    max-runs: 20
    per: day

outputs:
  - type: add-labels
    config:
      allowed: [bug, feature, question, docs, needs-repro]
  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true
      max: 1
```

### Locked Down (Enterprise)

```yaml
safety:
  strict: true
  stop-after: "+1y"
  lock-for-agent: true
  roles: [maintainer]
  rate-limit:
    max-runs: 5
    per: hour
  network:
    allowed:
      - "api.github.com"
  permissions:
    contents: read
    issues: write
    pull-requests: read

outputs:
  - type: create-discussion
    config:
      max: 1
      expires: "14d"
      close-older: true
  - type: add-labels
    config:
      allowed: [reviewed, needs-attention, compliant, non-compliant]
```

---

## The Missing `safe-outputs` Problem

> **Finding: 6 out of 79 production workflows have NO `safe-outputs:` defined at all** — the agent literally can't write results anywhere.

A workflow without safe outputs will run, consume model tokens, and then silently discard its work because it has no authorized output channel. This is one of the most common configuration mistakes.

> **Rule: Every workflow needs at least `create-issue` or `noop` as a safe output.**

```yaml
# ❌ Bad — no outputs defined, agent's work is lost
steps:
  - agent:
      prompt: Analyze the repository for security issues.

# ✅ Good — minimum viable output
steps:
  - agent:
      prompt: Analyze the repository for security issues.

outputs:
  - type: create-issue
    config:
      max: 1
      labels: ["automated"]
```

If the workflow is purely diagnostic (no side effects desired), use `noop` to explicitly acknowledge that no output is expected:

```yaml
outputs:
  - type: noop    # Workflow is intentionally output-free (e.g., dry-run testing)
```

*Source: Analysis of 79 production workflows*

---

## Common Gotchas

1. **Set `max` on every output.** Without it, there's no upper bound on what the agent creates.
2. **Set `stop-after` on every scheduled workflow.** Forgotten workflows are silent resource drains.
3. **Set `allowed` on every label output.** Agents are creative label inventors.
4. **Set `roles` on every slash command.** Otherwise any commenter can trigger your workflow.
5. **Set `hide-older-comments: true`** to prevent comment spam on long-lived issues.
6. **Default to `draft: true`** for all PR outputs — never auto-merge.
7. **Start restrictive, loosen as needed.** It's easier to add permissions than to clean up after a misconfigured workflow.
8. **Define at least one safe output.** Without it, the agent's work is silently discarded (see above).
