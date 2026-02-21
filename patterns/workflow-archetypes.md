# Workflow Archetypes — What type of workflow am I building?

## The 8 Archetypes

Every agentic workflow fits one of these eight archetypes. Start by identifying yours — it determines your trigger, output, state, and prompt structure.

| # | Archetype | Trigger | Output | State | Frequency |
|---|---|---|---|---|---|
| 1 | **Issue Triage** | `issues:[opened]` | Labels + Comment | Stateless | Event-driven |
| 2 | **CI Doctor** | `workflow_run(failure)` | Comment on PR | cache-memory | Event-driven |
| 3 | **Daily Improver** | `schedule:daily` | Draft PR | cache-memory | 1x/day |
| 4 | **Weekly Report** | `schedule:weekly` | Discussion | cache-memory | 1x/week |
| 5 | **Slash Command** | `slash_command` | Comment / Review | cache-memory | On-demand |
| 6 | **Moderation** | `issues/PR:[opened]` | Labels + Hide | Stateless | Event-driven |
| 7 | **Content Pipeline** | `dispatch` | Discussion → Dispatch | Chained | On-demand |
| 8 | **Enterprise SRE** | `schedule:weekly` | Discussion + Artifact | Keyed cache | 1x/week |

---

## Archetype 1: Issue Triage

> **"Classify and respond to every new issue automatically."**

### When to Use
- Open-source project with 5+ issues/day
- Issues need consistent labeling and first response
- Maintainers are overwhelmed with triage

### Architecture

```yaml
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        Triage this issue:
        1. Check for duplicates
        2. Classify as [bug, feature, question, docs]
        3. Add priority label
        4. Provide a helpful first response

outputs:
  - type: add-labels
    config:
      allowed: [bug, feature, question, docs, duplicate, needs-repro]
  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true

safety:
  rate-limit: { max-runs: 50, per: day }
```

### Key Decisions
- **Duplicate detection:** Do you search existing issues or just classify?
- **Auto-close:** Do you close obvious duplicates or just label them?
- **Response tone:** Friendly community bot or minimal triage label?

### Common Gotchas
- Without `allowed` labels, the agent invents creative labels
- Without `hide-older-comments`, re-triggered workflows spam the thread
- Test with edge cases: empty body, non-English, spam, very long issues

### Production Examples
- [appwrite/appwrite](https://github.com/appwrite/appwrite) — batch daily triage
- [apollographql/apollo](https://github.com/apollographql) — per-issue triage
- [apollographql/rover](https://github.com/apollographql/rover) — CLI-specific triage
- [Kong/kong](https://github.com/Kong/kong) — component-based routing

---

## Archetype 2: CI Doctor

> **"Diagnose CI failures and tell the developer what went wrong."**

### When to Use
- CI failures are frequent and varied
- Developers waste time reading raw logs
- Flaky tests need to be identified and tracked

### Architecture

```yaml
on:
  workflow_run:
    workflows: ["CI", "Build", "Tests"]
    types: [completed]
    # Filter to failures only in workflow logic

memory:
  type: cache

steps:
  - agent:
      model: claude-sonnet-4.5
      prompt: |
        A CI workflow failed. Diagnose it:
        1. Read the workflow run logs
        2. Check if this error signature is in memory (known flaky)
        3. Identify root cause
        4. Post a diagnosis on the associated PR

        If this is a new error pattern, save it to memory.

outputs:
  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true

safety:
  rate-limit: { max-runs: 20, per: hour }
```

### Key Decisions
- **Model:** claude-sonnet-4.5 for deep investigation, default for simple pattern matching
- **Flaky tracking:** Use cache-memory to identify recurring failures
- **Scope:** Diagnose only, or also suggest fixes with code?

### Common Gotchas
- Filter to failures only — don't trigger on successful runs
- Rate limit aggressively — CI failures can cascade
- Cache known flaky test patterns to avoid repeated analysis

### Production Example
- [JanDeDobbeleer/oh-my-posh](https://github.com/JanDeDobbeleer/oh-my-posh) — workflow-doctor with claude-sonnet-4.5

---

## Archetype 3: Daily Improver

> **"Make one small improvement to the codebase every day."**

### When to Use
- Gradual code quality improvement
- Test coverage expansion
- Accessibility, performance, or security hardening
- Tech debt reduction campaigns

### Architecture

```yaml
on:
  schedule:
    - cron: '0 9 * * 1-5'   # Weekdays at 9am UTC

memory:
  type: cache

steps:
  - agent:
      prompt: |
        Find ONE improvement to make today:
        1. Check memory for previously improved files (skip them)
        2. Scan the codebase for the highest-impact opportunity
        3. Make the change
        4. Run tests to verify
        5. Save the file path to memory

        Rules:
        - ONE improvement per run, not multiple
        - Must not break existing tests
        - Keep changes small and reviewable

outputs:
  - type: create-pull-request
    config:
      draft: true
      if-no-changes: ignore
      labels: ["automated", "improvement"]
      max: 1

safety:
  stop-after: "+90d"
```

### Key Decisions
- **Scope:** Code simplification? Test coverage? Docs? Pick one focus area.
- **Cadence:** Daily is aggressive — consider 3x/week for lower noise.
- **Review process:** Draft PRs need human reviewers assigned.

### Common Gotchas
- Without memory, the agent will "improve" the same file repeatedly
- Without `if-no-changes: ignore`, you get empty PRs
- Without `stop-after`, the workflow runs forever even after the campaign ends
- Always `draft: true` — automated code should never auto-merge

### Production Examples
- [BabylonJS](https://github.com/BabylonJS) — daily code improvements
- care_fe — daily test coverage expansion

---

## Archetype 4: Weekly Report

> **"Generate a recurring summary of project health, metrics, or activity."**

### When to Use
- Stakeholders need regular project visibility
- Metrics should be tracked week-over-week
- Team needs a digest of what happened

### Architecture

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'    # Monday 9am UTC

memory:
  type: cache
  retention-days: 35       # Keep 5 weeks of history

steps:
  - run: python fetch_metrics.py > /tmp/metrics.json
  - agent:
      prompt: |
        Generate a weekly health report:
        1. Read metrics from /tmp/metrics.json
        2. Compare to previous week (from memory)
        3. Highlight trends and anomalies
        4. Provide actionable recommendations
        5. Save this week's metrics to memory for next week

outputs:
  - type: create-discussion
    config:
      category: "Reports"
      title-prefix: "Weekly Health Report"
      close-older: true
      expires: "14d"

safety:
  stop-after: "+1y"
```

### Key Decisions
- **Data source:** Pre-fetch in run step or agent queries directly?
- **Comparison:** Week-over-week requires cache-memory or snapshot pattern
- **Audience:** Technical team (detailed) or leadership (executive summary)?

### Common Gotchas
- Use `create-discussion` NOT `create-issue` for reports
- Always `close-older: true` to avoid accumulating open discussions
- Set `retention-days` on cache to keep enough weeks for trend comparison
- Pre-fetch data in a `run` step for large datasets

### Production Examples
- org-health — organization-wide health metrics
- weekly-newsletter — team activity digest

---

## Archetype 5: Slash Command

> **"Let developers invoke AI tools on-demand via comments."**

### When to Use
- Interactive tools that users invoke when needed
- Ad-hoc analysis, planning, or review
- Tools that should only run when explicitly requested

### Architecture

```yaml
on:
  issue_comment:
    types: [created]
  # Filter for /command in workflow logic

memory:
  type: cache

steps:
  - agent:
      prompt: |
        The user invoked a command. Based on the command:

        /plan — Generate an implementation plan for this issue
        /nit — Leave nitpick review comments on this PR
        /feedback — Provide structured feedback

outputs:
  - type: add-comment
    config:
      target: triggering
      hide-older-comments: true

safety:
  roles: [maintainer, collaborator]
  rate-limit: { max-runs: 10, per: hour }
```

### Key Decisions
- **Command routing:** Single workflow with multiple commands or one workflow per command?
- **Permissions:** Who can invoke? Maintainers only or all collaborators?
- **Output type:** Comment for analysis, review comments for code feedback

### Common Gotchas
- **Always restrict `roles`** — without it, any commenter can trigger
- **Always `hide-older-comments`** — users will invoke multiple times
- Rate limit per user, not just globally

### Production Examples
- `/plan` — implementation planning
- `/nit` — nitpick code review
- `/grumpy` — opinionated review (personality-driven)
- `/feedback` — structured feedback

---

## Archetype 6: Moderation

> **"Automatically detect and handle spam, abuse, or policy violations."**

### When to Use
- High-traffic repos with spam problems
- Content policy enforcement
- Automated quality gates on new content

### Architecture

```yaml
on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

steps:
  - agent:
      model: gpt-5.1-codex-mini     # Fast classification
      prompt: |
        Classify this content:
        - spam: Promotional, irrelevant, or bot-generated
        - abuse: Violates code of conduct
        - low-quality: Missing required information
        - valid: Legitimate contribution

        If spam or abuse, add the label and minimize the content.
        If low-quality, comment asking for more information.
        If valid, do nothing.

outputs:
  - type: add-labels
    config:
      allowed: [spam, abuse, low-quality]

safety:
  strict: true
  rate-limit: { max-runs: 100, per: hour }
```

### Key Decisions
- **Model:** codex-mini for speed (classification doesn't need deep reasoning)
- **Action on detection:** Label only, or also hide/close?
- **False positive handling:** How does a human override?

### Common Gotchas
- Use a fast model (codex-mini) — moderation must be near-instant
- Always have a human override mechanism (label removal triggers unhide)
- Log false positives to improve the prompt over time
- Be careful with auto-close — false positives alienate real users

### Production Example
- [f/prompts.chat](https://github.com/f/awesome-chatgpt-prompts) — ai-moderator for spam detection

---

## Archetype 7: Content Pipeline

> **"Chain multiple workflows to produce, refine, and publish content."**

### When to Use
- Multi-stage content creation (draft → review → publish)
- Workflows that need different agents/models per stage
- Complex pipelines where each stage has different requirements

### Architecture

```yaml
# Stage 1: Draft
on:
  workflow_dispatch:
    inputs:
      topic:
        required: true

steps:
  - agent:
      prompt: |
        Write a technical blog post draft about: ${{ inputs.topic }}

outputs:
  - type: create-discussion
    config:
      category: "Drafts"
      title-prefix: "Draft"
  - type: dispatch-workflow
    config:
      workflow: blog-linker.yml
      inputs:
        draft_discussion_id: "${{ outputs.discussion_id }}"
```

```yaml
# Stage 2: Link & SEO
on:
  workflow_dispatch:
    inputs:
      draft_discussion_id:
        required: true

steps:
  - agent:
      prompt: |
        Read the draft from discussion ${{ inputs.draft_discussion_id }}.
        Add internal links, SEO metadata, and cross-references.

outputs:
  - type: create-pull-request
    config:
      draft: true
      title-prefix: "[blog] "
```

### Key Decisions
- **Handoff mechanism:** dispatch-workflow, discussion, or artifacts?
- **Human-in-the-loop:** Where do humans review/approve?
- **Failure handling:** What happens if stage 2 fails?

### Common Gotchas
- Each stage needs its own error handling — don't assume upstream succeeded
- Use discussions for visible handoff points where humans can intervene
- Keep each stage focused — don't try to do everything in one workflow

### Production Example
- blog-drafter → blog-linker pipeline

---

## Archetype 8: Enterprise SRE

> **"Monitor infrastructure, track SLOs, and generate compliance reports."**

### When to Use
- SLO tracking and reporting
- Multi-service health monitoring
- Compliance auditing with evidence collection
- Incident correlation and analysis

### Architecture

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'    # Monday 9am UTC

memory:
  type: cache
  retention-days: 35        # 5 weeks of SLO history

steps:
  - run: |
      az login --service-principal \
        -u ${{ secrets.AZURE_CLIENT_ID }} \
        -p ${{ secrets.AZURE_CLIENT_SECRET }} \
        --tenant ${{ secrets.AZURE_TENANT_ID }}
      python fetch_slo_data.py > /tmp/slo-data.json
      python generate_charts.py --input /tmp/slo-data.json --output /tmp/charts/

  - agent:
      model: claude-opus-4.6
      prompt: |
        Generate the weekly SLO compliance report.

        ## Data Sources
        - /tmp/slo-data.json — SLO metrics for all services
        - /tmp/charts/ — Pre-generated charts

        ## Report Structure
        1. Executive Summary (3 sentences)
        2. SLO Compliance Table (per service)
        3. Incidents & Correlations
        4. Trend Analysis (vs previous weeks from memory)
        5. Risk Assessment & Recommendations

        ## Rules
        - Use keyed memory: "slo:{service}:{week}" for history
        - Flag any service below 99.9% SLO target
        - Correlate error spikes with deployment events
        - DO NOT access external services — all data is pre-fetched

outputs:
  - type: create-discussion
    config:
      category: "SLO Reports"
      title-prefix: "Weekly SLO Report"
      close-older: true
      expires: "30d"
  - type: upload-asset
    config:
      path: /tmp/charts/

safety:
  strict: true
  lock-for-agent: true
  stop-after: "+1y"
  network:
    allowed: ["api.github.com"]
  permissions:
    contents: read
    discussions: write
```

### Key Decisions
- **Model:** claude-opus-4.6 for complex analysis and correlation
- **Data ingestion:** Pre-step with service authentication
- **State:** Keyed cache-memory for per-service trend tracking
- **Charts:** Generate in pre-step, upload as assets

### Common Gotchas
- Pre-fetch ALL data — don't let the agent call cloud APIs directly
- Use `strict: true` and restricted network for enterprise compliance
- Keyed memory with retention avoids unbounded state growth
- Charts should be generated by code (matplotlib, plotly), not the agent

### Production Example
- An enterprise SRE workflow — Azure SLO monitoring with weekly reports

---

## Picking Your Archetype

```
What does your workflow do?

├── Respond to new issues?
│   ├── Classify and label → Issue Triage (1)
│   └── Detect spam/abuse → Moderation (6)
│
├── Respond to CI/CD events?
│   └── Diagnose failures → CI Doctor (2)
│
├── Run on a schedule?
│   ├── Make code changes → Daily Improver (3)
│   ├── Generate reports → Weekly Report (4)
│   └── Monitor infrastructure → Enterprise SRE (8)
│
├── Triggered by humans on-demand?
│   ├── Via comment → Slash Command (5)
│   └── Via UI → Content Pipeline (7) or workflow_dispatch
│
└── Chain multiple stages?
    └── Content Pipeline (7)
```

---

## Timeout Guidance

> Timeouts in production workflows range from 5 to 120 minutes with no clear correlation to complexity. Use these recommendations by archetype:

| Archetype | Recommended Timeout | Rationale |
|---|---|---|
| Simple triage / labeling | 10–15 min | Classification is fast; if it's not done in 15 min, something is wrong |
| Single-topic report | 30 min | One data source, one output — straightforward |
| Multi-source data + narrative | 60 min | Multiple pre-fetches, cross-referencing, long-form writing |
| Data-heavy + opus model | 60–120 min | Opus is slower; large data analysis needs room |

```yaml
# Set timeout in the workflow
timeout-minutes: 30    # Adjust based on archetype above
```

**Rule of thumb:** Start with the recommended timeout. If runs consistently finish in <50% of the timeout, lower it. If runs hit the timeout, either the data is too large (add a pre-step) or the prompt needs to be more focused.

*Source: Analysis of 79 production workflows*

---

## Additional Archetypes from Production

These six sub-archetypes emerged from production workflow analysis. Each is a variant of the core eight, specialized for a common real-world pattern.

### Sub-archetype: Team Activity Report

> Prefetch data → read files → write narrative issue

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'    # Weekly

steps:
  - run: |
      python fetch_team_activity.py > /tmp/activity.json
      sleep 1
      python fetch_pr_stats.py > /tmp/prs.json
  - agent:
      model: claude-opus-4.6
      prompt: |
        Write a narrative team activity report from /tmp/activity.json and /tmp/prs.json.
        DO NOT call the GitHub API — all data is pre-fetched.

timeout-minutes: 60
```

**Key traits:** Opus model for narrative quality, pre-fetched data, 60-minute timeout.

### Sub-archetype: Org Health Scan

> Prefetch metrics → analyze → create issue

```yaml
on:
  schedule:
    - cron: '0 6 * * 1'

steps:
  - run: python fetch_org_metrics.py > /tmp/metrics.json
  - agent:
      prompt: |
        Analyze org health metrics from /tmp/metrics.json.
        Flag repos with declining activity or missing CI.

timeout-minutes: 30
```

**Key traits:** Default model (metrics analysis is mechanical), 30-minute timeout.

### Sub-archetype: Feedback Triage

> Read issue → classify → add labels/comment

```yaml
on:
  issues:
    types: [opened]

steps:
  - agent:
      prompt: |
        Read this feedback issue. Classify as: [praise, bug, feature-request, confusion].
        Add the appropriate label and respond with acknowledgment.

timeout-minutes: 10
```

**Key traits:** Default model, stateless, fast — 10-minute timeout.

### Sub-archetype: Compliance Checker

> Scan repo → evaluate → create issue

```yaml
on:
  schedule:
    - cron: '0 8 * * 1-5'

steps:
  - run: |
      python scan_repos_compliance.py > /tmp/compliance.json
  - agent:
      prompt: |
        Review compliance scan results in /tmp/compliance.json.
        Create an issue for each repo that fails checks.

timeout-minutes: 30
```

**Key traits:** Default model, pre-fetched scan data, 30-minute timeout.

### Sub-archetype: Sentiment Analysis

> Prefetch discussions → analyze tone → create issue

```yaml
on:
  schedule:
    - cron: '0 10 * * 1'

steps:
  - run: python fetch_discussions.py > /tmp/discussions.json
  - agent:
      model: claude-opus-4.6
      prompt: |
        Analyze community sentiment from /tmp/discussions.json.
        Identify concerning trends, frustrated users, or praise patterns.
        Write a nuanced summary — tone matters more than counts.

timeout-minutes: 45
```

**Key traits:** Opus model (nuance in sentiment detection), 45-minute timeout.

### Sub-archetype: Data Pipeline

> Prefetch → transform → write to file

```yaml
on:
  schedule:
    - cron: '0 5 * * *'

steps:
  - run: |
      python fetch_raw_data.py > /tmp/raw.json
      sleep 1
      python transform_data.py /tmp/raw.json > /tmp/transformed.json
  - agent:
      prompt: |
        Validate the transformed data in /tmp/transformed.json.
        Check for anomalies, missing fields, or unexpected values.
        Write a summary to /tmp/validation-report.md.

timeout-minutes: 15
```

**Key traits:** Default model, mostly scripted pipeline with agent validation, 15–30 minute timeout.

---

## Archetype Comparison: At a Glance

| Aspect | Triage | CI Doctor | Improver | Report | Slash Cmd | Moderation | Pipeline | SRE |
|--------|--------|-----------|----------|--------|-----------|------------|----------|-----|
| **Trigger** | Issue | WF Run | Cron | Cron | Comment | Issue/PR | Dispatch | Cron |
| **Model** | Default | Sonnet | Default | Default | Default | Codex-mini | Default | Opus |
| **State** | None | Cache | Cache | Cache | Cache | None | Chained | Keyed |
| **Max output** | 1 | 1 | 1 | 1 | 1 | 1 | Varies | 1 |
| **stop-after** | — | — | +90d | +1y | — | — | — | +1y |
| **Complexity** | ★★☆ | ★★★ | ★★☆ | ★★☆ | ★★☆ | ★☆☆ | ★★★ | ★★★★ |

---

## Starter Templates

Each archetype above includes a complete, copy-pasteable architecture block. To get started:

1. **Identify your archetype** using the decision tree above
2. **Copy the architecture block** from the relevant section
3. **Customize** the prompt, labels, and safety settings for your repo
4. **Test 3-5 times** before enabling in production
5. **Add guardrails** based on what you observe in testing

See also:
- [Trigger Selection](./trigger-selection.md) — deep dive on trigger types
- [Output Selection](./output-selection.md) — deep dive on output types
- [State Management](./state-management.md) — deep dive on memory patterns
- [Model Selection](./model-selection.md) — deep dive on model choices
- [Prompt Structure](./prompt-structure.md) — deep dive on prompt writing
- [Safety Configuration](./safety-configuration.md) — deep dive on safety settings
- [Shared Components](./shared-components.md) — deep dive on reusable modules
- [Data Ingestion](./data-ingestion.md) — deep dive on feeding data to workflows
