# State Management — How do I remember things across runs?

## The Problem

Agentic workflows are stateless by default — each run starts fresh. But many workflows need memory:
- "Don't re-review files I already reviewed"
- "Compare this week's metrics to last week's"
- "Track progress on a multi-day improvement campaign"

---

## Decision Matrix

| Pattern | Persistence | Scope | Complexity | Best For |
|---|---|---|---|---|
| **Stateless** | None | Single run | ★☆☆ | Triage, labeling, one-shot analysis |
| **cache-memory** | Cross-run | Per workflow | ★★☆ | Review history, seen items |
| **cache-memory (keyed)** | Cross-run | Per key | ★★☆ | Multi-resource tracking |
| **repo-memory** | Permanent | Per repo/branch | ★★★ | Compliance, accumulated knowledge |
| **Tracking issue** | Permanent | Per issue | ★★☆ | Multi-day campaigns with visibility |
| **Discussion as state** | Permanent | Per discussion | ★★☆ | Phase handoffs between workflows |
| **Pre-step snapshot** | Ephemeral | Single run | ★★☆ | Week-over-week diffs |

---

## Pattern 1: Stateless (No Memory)

**When:** Each run is independent. The agent doesn't need to know about previous runs.

**This is the default and the most common pattern.** Don't add state unless you need it.

### Production Examples

Most triage workflows are stateless:

```yaml
# Every issue is triaged independently
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        Triage this issue. Classify and label it.
        # No memory needed — each issue is independent
```

**When to stay stateless:**
- Issue triage (each issue is independent)
- PR review (each PR is independent)
- Slash commands (each invocation is independent)
- One-shot reports (no comparison to previous runs)

---

## Pattern 2: cache-memory

**When:** The agent needs to remember what it's already seen or done across runs.

### How It Works

```yaml
memory:
  type: cache
  retention-days: 30    # Optional — auto-expire after N days
```

The platform provides a key-value cache scoped to the workflow. The agent can read and write to it between runs.

### Production Example — workflow-doctor

[JanDeDobbeleer/oh-my-posh](https://github.com/JanDeDobbeleer/oh-my-posh) — remembers which failures it's already diagnosed:

```yaml
memory:
  type: cache

steps:
  - agent:
      prompt: |
        Check if this workflow failure has been seen before.
        - If this error signature is in memory, skip it (already diagnosed)
        - If new, diagnose and save the error signature to memory
```

### Production Example — nitpick-reviewer

Remembers which files have been reviewed to avoid duplicate feedback:

```yaml
memory:
  type: cache

steps:
  - agent:
      prompt: |
        Review this PR. Before reviewing each file:
        1. Check memory for "reviewed:{filepath}:{sha}"
        2. If found, skip the file (already reviewed)
        3. If not found, review it and save the key to memory
```

**Gotchas:**
- Cache is eventually consistent — don't rely on it for critical state
- Cache may be evicted under memory pressure
- Always design workflows to work correctly even if the cache is empty

---

## Pattern 3: cache-memory with Key and Retention

**When:** You track multiple resources and need organized, auto-expiring state.

### Production Example — Enterprise SRE Workflow

Tracks SLO compliance per service with 35-day retention:

```yaml
memory:
  type: cache
  retention-days: 35

steps:
  - agent:
      prompt: |
        For each monitored service:
        1. Fetch current SLO metrics
        2. Read previous metrics from memory (key: "slo:{service-name}")
        3. Compare and flag regressions
        4. Save current metrics to memory (key: "slo:{service-name}")

        Use structured keys:
        - "slo:api-gateway" → latest API gateway SLO data
        - "slo:auth-service" → latest auth service SLO data
        - "alert:api-gateway:2024-01-15" → alert history
```

**Key naming conventions:**
```
{category}:{resource}              → "slo:api-gateway"
{category}:{resource}:{date}       → "alert:api-gateway:2024-01-15"
{category}:{resource}:{sha}        → "reviewed:src/auth.ts:abc123"
```

**Retention guidelines:**
| Use Case | Retention |
|---|---|
| PR review state | 7-14 days |
| Weekly reports | 30-35 days |
| SLO tracking | 35-90 days |
| Long-term trends | 90+ days |

---

## Pattern 4: repo-memory on Dedicated Branch

**When:** You need permanent, version-controlled state that survives cache evictions.

### How It Works

The agent writes state files to a dedicated branch (e.g., `copilot/memory`). This is Git-backed — it's permanent, auditable, and survives any cache issues.

### Production Example — delight

UX improvement tracker that accumulates knowledge over time:

```yaml
memory:
  type: repo
  branch: copilot/delight-memory

steps:
  - agent:
      prompt: |
        You are a UX improvement agent. You maintain a knowledge base on
        the copilot/delight-memory branch.

        Files you manage:
        - patterns.json — UX patterns you've identified
        - improvements.md — log of improvements made
        - skip-list.json — components to skip (already optimized)

        1. Read your knowledge base from the memory branch
        2. Scan the codebase for UX improvement opportunities
        3. Skip anything in skip-list.json
        4. Create PRs for improvements
        5. Update your knowledge base with findings
```

### Production Example — security-compliance

Tracks compliance state across audits:

```yaml
memory:
  type: repo
  branch: copilot/compliance

steps:
  - agent:
      prompt: |
        Maintain compliance records on the copilot/compliance branch:
        - audit-log.json — all audit findings and resolutions
        - exceptions.json — approved exceptions with expiry dates
        - last-scan.json — timestamp and results of last scan
```

**Gotchas:**
- The memory branch will accumulate commits — consider squashing periodically
- Don't store sensitive data (secrets, PII) in repo memory
- Use `.json` files for structured data the agent can easily read/write

---

## Pattern 5: Tracking Issue (Find-or-Create)

**When:** You want visible progress tracking that humans can follow and interact with.

### Production Example — daily-playwright-improver

Creates or finds a tracking issue for a multi-day improvement campaign:

```yaml
steps:
  - agent:
      prompt: |
        Find or create a tracking issue titled "[Playwright] Test Improvement Tracker".

        ## If the issue exists:
        1. Read the checklist in the issue body
        2. Find the next unchecked item
        3. Work on that item
        4. Update the issue body (check off completed items)
        5. Add a comment with what you did today

        ## If the issue doesn't exist:
        1. Scan the test suite for improvement opportunities
        2. Create the tracking issue with a checklist of all improvements
        3. Work on the first item
        4. Check it off

        ## Issue body format:
        ```
        ## Test Improvements
        - [x] Improve login flow tests (completed 2024-01-15)
        - [x] Add error boundary tests (completed 2024-01-16)
        - [ ] Refactor navigation tests
        - [ ] Add accessibility tests
        - [ ] Improve test data factories
        ```
```

**Why this pattern is powerful:**
- Humans can see progress at a glance
- Humans can reorder, add, or remove items
- The agent adapts to human edits
- It's a natural collaboration point

---

## Pattern 6: Discussion as State Between Phases

**When:** One workflow's output becomes another workflow's input, and you need a visible handoff point.

### Production Example — ksail/daily-backlog-burner

Phase 1 creates a discussion with a plan, Phase 2 reads it and executes:

```yaml
# Phase 1: Planning (runs at 6am)
steps:
  - agent:
      prompt: |
        Analyze the backlog and create a prioritized plan for today.
        Output the plan as a structured discussion.

outputs:
  - type: create-discussion
    config:
      category: "Daily Plans"
      title-prefix: "Daily Plan"
      close-older: true
```

```yaml
# Phase 2: Execution (runs at 9am)
steps:
  - run: |
      gh api graphql -f query='{ repository(owner:"owner", name:"repo") {
        discussions(categoryId:"...", first:1, orderBy:{field:CREATED_AT, direction:DESC}) {
          nodes { body }
        }
      }}' --jq '.data.repository.discussions.nodes[0].body' > /tmp/todays-plan.md

  - agent:
      prompt: |
        Read today's plan from /tmp/todays-plan.md.
        Execute the top 3 items from the plan.
        Create PRs for each completed item.
```

**Why discussions work for handoffs:**
- Both humans and agents can read/write them
- They're timestamped and threaded
- `close-older: true` keeps only the latest active

---

## Pattern 7: Pre-step Snapshot for Diffs

**When:** You need to compare current state to a previous point in time (week-over-week, day-over-day).

### Production Example — weekly-newsletter Week-over-Week

```yaml
steps:
  # Snapshot: Fetch last week's data from cache or API
  - run: |
      # Get last week's metrics (saved from previous run)
      gh api /repos/owner/repo/actions/cache \
        --jq '.actions_caches[] | select(.key == "newsletter-metrics-prev")' \
        > /tmp/last-week.json || echo '{}' > /tmp/last-week.json

      # Get this week's metrics
      python fetch_metrics.py > /tmp/this-week.json

      # Save this week's metrics as "previous" for next run
      # (done via actions/cache in the workflow)

  - agent:
      prompt: |
        Compare this week's metrics (/tmp/this-week.json) to last week's
        (/tmp/last-week.json).

        Highlight:
        - Metrics that improved (↑ with green)
        - Metrics that regressed (↓ with red)
        - New records or milestones
```

---

## Decision Flowchart

```
Does the workflow need memory at all?
├── No → Stateless (Pattern 1)
└── Yes
    ├── Just avoid re-processing?
    │   └── cache-memory (Pattern 2)
    ├── Track multiple resources?
    │   └── cache-memory with keys (Pattern 3)
    ├── Need permanent, auditable state?
    │   └── repo-memory on branch (Pattern 4)
    ├── Need visible progress tracking?
    │   └── Tracking issue (Pattern 5)
    ├── Need handoff between workflow phases?
    │   └── Discussion as state (Pattern 6)
    └── Need before/after comparison?
        └── Pre-step snapshot (Pattern 7)
```

---

## Common Gotchas

1. **Default to stateless.** Most workflows don't need memory. Adding state adds complexity.
2. **Cache is not a database.** It can be evicted. Always handle cache misses gracefully.
3. **Repo memory is permanent.** Don't store ephemeral data in Git branches — use cache for that.
4. **Tracking issues are collaborative.** Humans will edit them — design your agent to handle unexpected changes.
5. **Retention matters.** Set `retention-days` on cache entries or they'll accumulate forever.
6. **State creates coupling.** If your workflow depends on state from a previous run, what happens when the state is corrupt or missing? Always have a fallback.
