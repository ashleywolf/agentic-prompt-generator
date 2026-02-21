# Discovery Methodology

How we find and verify the public repos powering this project's data.

## 5-Step Scanning Process

### Step 1: Search for Candidate Repos

We search GitHub for repos containing agentic workflow files using these queries:

```
# Primary: find .md files in .github/workflows (the agentic workflow convention)
path:.github/workflows extension:md

# Narrower searches for specific workflow patterns
path:.github/workflows/copilot extension:md
path:.github/copilot
```

These queries return repos that have Markdown files inside `.github/workflows/`, which is the file convention for GitHub Copilot agentic workflows (as opposed to `.yml`/`.yaml` for traditional GitHub Actions).

### Step 2: Verify Visibility

Every candidate repo is checked to confirm it is **public**:

```bash
gh api "repos/{owner}/{repo}" --jq '.visibility'
```

Only repos returning `"public"` are included. Any repo that returns a 404 or `"private"` / `"internal"` is excluded. This ensures every data point in `scan-results.json` is independently verifiable by anyone.

### Step 3: Extract Workflow Metadata

For each public repo, we parse every `.md` file in `.github/workflows/` and extract:

| Field | Source |
|-------|--------|
| `name` | Filename (e.g., `issue-triage.md` → `issue-triage`) |
| `triggers` | YAML front matter or compiled workflow config |
| `model` | Explicit `model:` field if set (most use default) |
| `has_pre_steps` | Whether bash steps run before the agent |
| `stop_after` | Time limit if configured (e.g., `+48h`) |
| `source_available` | Whether the `.md` source is readable |

### Step 4: Verify Activity

Each repo's workflows are checked for recent runs using the GitHub Actions API:

```bash
gh api "repos/{owner}/{repo}/actions/runs?per_page=10" \
  --jq '.workflow_runs[] | {id, conclusion, created_at}'
```

A repo is marked `"active"` if it has at least one workflow run in the last 90 days. Repos with valid workflow files but no recent runs are marked `"inactive"` and still included in the dataset.

For each workflow run, we record:
- `conclusion` (success, failure, cancelled)
- `created_at` and `updated_at` timestamps
- Computed `success_rate` (e.g., `"8/8"`)

### Step 5: Compile Results

All data is written to [`data/scan-results.json`](data/scan-results.json) with this structure:

```json
{
  "metadata": {
    "scanned_at": "2026-02-21T06:22:55Z",
    "total_repos": 269,
    "total_workflows": 679,
    "active_repos": 246
  },
  "repos": {
    "owner/repo": {
      "url": "https://github.com/owner/repo",
      "stars": 1234,
      "description": "...",
      "status": "active",
      "recent_runs": 10,
      "workflows": [
        {
          "name": "issue-triage",
          "file": "issue-triage.md",
          "triggers": ["issues"],
          "has_pre_steps": false,
          "source_available": true,
          "success_rate": "8/10",
          "last_conclusion": "success"
        }
      ]
    }
  }
}
```

## Current Numbers

| Metric | Value |
|--------|-------|
| Repos discovered | 269 |
| Repos active (last 90 days) | 246 |
| Total workflows | 679 |
| Workflows with readable source | 661 |
| Unique workflow names | 398 |
| Last scan | 2026-02-21 |

## What Gets Excluded

- **Private/internal repos** — visibility must be `"public"`
- **Repos with no `.md` workflow files** — traditional `.yml` Actions are out of scope
- **Forks with no modifications** — if the workflow files are identical to the upstream, only the upstream is counted
- **Broken/unparseable files** — 18 workflows had unreadable source and are noted as `source_available: false`

## Reproducibility

Anyone can reproduce the scan:

```bash
# Clone this repo
git clone https://github.com/YOUR_ORG/agentic-prompt-generator
cd agentic-prompt-generator

# Run the scan (requires gh CLI, authenticated)
bash scripts/scan.sh

# Results written to data/scan-results.json
```

The scan requires a GitHub personal access token with `public_repo` scope. No private data is accessed.
