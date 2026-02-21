# Data Ingestion — How do I feed data to my workflow?

## The Problem

Agents hit hard limits when they try to fetch data themselves:
- API pagination caps out (500+ results = timeout or token explosion)
- Repo clones take too long inside an agent turn
- Service authentication requires credentials the agent shouldn't hold
- Large datasets blow up the context window

**The solution:** Move heavy data fetching into a **pre-step** before the agent runs, then point the agent at the results.

---

## Decision Matrix

| Pattern | When to Use | Data Size | Latency | Complexity |
|---|---|---|---|---|
| **Agent direct** | <100 items, simple API | Small | Low | ★☆☆ |
| **Pre-step bash fetch** | CLI tools, structured output | Medium | Medium | ★★☆ |
| **Pre-step Python script** | Complex transforms, multiple sources | Large | Medium | ★★☆ |
| **Pre-step repo clone** | Need full repo context | Large | High | ★★☆ |
| **Pre-step sparse checkout** | Need specific dirs from large repo | Medium | Medium | ★★★ |
| **Pre-step service login** | Cloud services, databases | Varies | Medium | ★★★ |
| **Agent with guardrails** | Pre-fetched data + agent analysis | Large | Low (agent) | ★★☆ |

---

## Pattern 1: Agent Direct

**When:** The agent can query what it needs in <100 items, no pagination required.

**Production example:** [appwrite/issue-triage](https://github.com/appwrite) — agent searches GitHub issues directly.

```yaml
steps:
  - agent:
      prompt: |
        Search for similar issues using the GitHub search API.
        Only search the top 50 results — do not paginate beyond that.
```

**Gotchas:**
- Set explicit limits ("top 50", "last 7 days") or the agent will try to fetch everything
- Works best with GitHub's built-in search, not raw API pagination

---

## Pattern 2: Pre-step Bash Fetch

**When:** A CLI tool can dump structured data to a file.

**Production example:** [github/gh-aw portfolio-analyst](https://github.com/github/gh-aw) — fetches 30 days of GitHub Actions logs.

```yaml
steps:
  - run: |
      ./gh-aw logs --start-date -30d --format json -o /tmp/actions-logs.json
      echo "Fetched $(wc -l < /tmp/actions-logs.json) log entries"

  - agent:
      prompt: |
        Analyze the Actions workflow data in /tmp/actions-logs.json.

        ## Guardrails
        - DO NOT call `gh aw logs` yourself — all data is pre-fetched
        - Read from /tmp/actions-logs.json only
```

**Gotchas:**
- Always echo a count/summary so you can debug empty files
- Always add a guardrail telling the agent NOT to re-fetch

---

## Pattern 3: Pre-step Python Script

**When:** You need to merge multiple APIs, transform data, or handle complex pagination.

**Production example:** weekly-newsletter — aggregates standup data from multiple sources.

```yaml
steps:
  - run: |
      python fetch_standup_data.py > /tmp/data.json
      python fetch_pr_metrics.py >> /tmp/metrics.json

  - agent:
      prompt: |
        You are a newsletter writer. Your data sources are:
        - /tmp/data.json — standup updates from this week
        - /tmp/metrics.json — PR merge times and review stats

        Write a concise weekly newsletter summarizing team activity.
```

**Minimal example — custom fetcher:**

```python
# fetch_standup_data.py
import json, subprocess

result = subprocess.run(
    ["gh", "api", "/repos/owner/repo/issues", "--paginate", "-q", ".[].title"],
    capture_output=True, text=True
)
data = [{"title": line} for line in result.stdout.strip().split("\n")]
print(json.dumps(data, indent=2))
```

**Gotchas:**
- Pin your Python dependencies or use `uv run` for reproducibility
- Write to `/tmp/` — it's ephemeral and safe

---

## Pattern 4: Pre-step Repo Clone

**When:** The agent needs to analyze source code, configs, or docs from another repo.

**Production example:** cli-bug-report — clones the CLI repo for code analysis.

```yaml
steps:
  - run: |
      git clone --depth 1 https://github.com/owner/repo.git /tmp/repo
      echo "Cloned repo: $(du -sh /tmp/repo | cut -f1)"

  - agent:
      prompt: |
        Analyze the codebase in /tmp/repo to investigate this bug report.
        Focus on the src/ directory for relevant code paths.
```

**Gotchas:**
- **Always use `--depth 1`** — full history is never needed and adds minutes
- For private repos, ensure the workflow has appropriate token permissions
- Large repos (>1GB) may time out — use sparse checkout instead

---

## Pattern 5: Pre-step Sparse Checkout

**When:** You only need specific directories from a large monorepo.

**Production example:** [daily-playwright-improver](https://github.com) — only needs `src/` and `tests/` from a large repo.

```yaml
steps:
  - run: |
      git clone --filter=blob:none --sparse https://github.com/owner/repo.git /tmp/repo
      cd /tmp/repo
      git sparse-checkout init --cone
      git sparse-checkout add src tests
      echo "Sparse checkout: $(find . -name '*.ts' | wc -l) TypeScript files"

  - agent:
      prompt: |
        Review the Playwright tests in /tmp/repo/tests/ and suggest improvements.
        Reference implementation code is in /tmp/repo/src/.
```

**Gotchas:**
- `--filter=blob:none` + `--sparse` is the fastest combo
- You must `sparse-checkout init --cone` before `sparse-checkout add`
- Verify the checkout worked — sparse checkout silently ignores bad paths

---

## Pattern 6: Pre-step Service Login

**When:** The agent needs data from a cloud service (Azure, AWS, Datadog, etc.).

**Production example:** An enterprise SRE workflow — authenticates to Azure for SLO data.

```yaml
steps:
  - run: |
      az login --service-principal \
        -u ${{ secrets.AZURE_CLIENT_ID }} \
        -p ${{ secrets.AZURE_CLIENT_SECRET }} \
        --tenant ${{ secrets.AZURE_TENANT_ID }}
      az monitor metrics list \
        --resource ${{ vars.APP_RESOURCE_ID }} \
        --metric "Http5xx" \
        --interval PT1H \
        --start-time $(date -d '-7 days' -u +%Y-%m-%dT%H:%M:%SZ) \
        > /tmp/slo-metrics.json

  - agent:
      prompt: |
        Analyze the SLO metrics in /tmp/slo-metrics.json.
        Flag any periods where error rate exceeded 0.1%.
```

**Gotchas:**
- **Never pass credentials to the agent** — authenticate in the pre-step
- Use `--service-principal` not interactive login
- Store secrets in GitHub Secrets, reference via `${{ secrets.* }}`

---

## Pattern 7: Agent with Guardrails

**When:** You pre-fetch data AND need the agent to do additional targeted lookups.

**Production example:** [portfolio-analyst](https://github.com/github/gh-aw) — pre-fetched bulk data + agent reads files.

```yaml
steps:
  - run: |
      ./gh-aw logs --start-date -30d -o /tmp/actions-data/
      ./gh-aw billing --format json > /tmp/billing.json

  - agent:
      prompt: |
        You are a portfolio analyst reviewing GitHub Actions usage.

        ## Data Sources
        - /tmp/actions-data/ — 30 days of workflow run logs
        - /tmp/billing.json — current billing data

        ## Rules
        - DO NOT call `gh aw logs` or `gh aw billing` — data is pre-fetched
        - DO NOT make any API calls to fetch additional data
        - You MAY use `jq` to query the JSON files
        - You MAY use `wc`, `sort`, `uniq` for analysis
```

---

## Quick Reference: Which Pattern?

```
Need data from GitHub API?
  ├── <100 items → Agent Direct
  └── 100+ items → Pre-step Bash (gh api --paginate)

Need data from external service?
  ├── Has CLI tool → Pre-step Bash
  ├── Complex transforms → Pre-step Python
  └── Requires auth → Pre-step Service Login

Need source code?
  ├── Small repo (<100MB) → Pre-step Repo Clone (--depth 1)
  └── Large repo / specific dirs → Pre-step Sparse Checkout

Already pre-fetched but agent needs more?
  └── Agent with Guardrails (explicit DO NOT rules)
```

---

## The 10KB MCP Payload Limit

> **Finding: 45 out of 79 production workflows don't prefetch data.** The agent discovers everything via MCP tool calls at runtime.

This causes three cascading failures:

1. **Payload too large.** MCP responses over ~10KB are rejected: `"payload was too large for an MCP response"`. A single `gh api` search returning 200+ results will hit this.
2. **Empty results from narrow searches.** To avoid the size limit, agents narrow their queries — and get `total_count: 0`. Now they're stuck.
3. **Turn waste.** The agent burns 5–10 turns on data gathering instead of reasoning about the data.

### The 3-Search Rule

> **Rule: If a workflow needs data from more than 3 API searches, add a `steps:` pre-step with a script that fetches data deterministically.**

```yaml
# ❌ Bad — agent discovers data via 8+ MCP searches
steps:
  - agent:
      prompt: |
        Find all repos in org X with >100 stars, then find their
        top contributors, then find open issues labeled "help wanted"...

# ✅ Good — pre-step fetches deterministically, agent reasons
steps:
  - run: |
      gh api --paginate "/orgs/X/repos?sort=stars&per_page=100" > /tmp/repos.json
      sleep 1
      gh api --paginate "/orgs/X/members" > /tmp/members.json
      echo "Fetched $(jq length /tmp/repos.json) repos, $(jq length /tmp/members.json) members"
  - agent:
      prompt: |
        Analyze org data from /tmp/repos.json and /tmp/members.json.
        DO NOT call the GitHub API — all data is pre-fetched.
```

### Rate Limit Delays

When a workflow has more than 3 search patterns in its pre-step, always include a delay between API calls to avoid rate limiting:

```yaml
steps:
  - run: |
      gh api "/orgs/X/repos" > /tmp/repos.json
      sleep 2
      gh api "/orgs/X/members" > /tmp/members.json
      sleep 2
      gh api "/orgs/X/teams" > /tmp/teams.json
```

> **Rule: Always include "Add a 1–2 second delay between API calls" in the prompt or pre-step when the workflow has >3 search patterns.**

*Source: Analysis of 79 production workflows*

---

## Common Gotchas

1. **Always tell the agent where the data is.** Don't assume it knows — be explicit: "Read from /tmp/data.json"
2. **Always tell the agent what NOT to do.** Without guardrails, agents will re-fetch data you already provided.
3. **Always verify the pre-step worked.** Echo file sizes, line counts, or record counts.
4. **Write to `/tmp/`** — it's ephemeral and won't pollute the workspace.
5. **Pre-steps run as the workflow runner** — they have full shell access, unlike the agent which may be sandboxed.
