# Discovery Methodology

How we found 120 repos with 188 agentic workflows across GitHub.

## The Signal: `.lock.yml` Files

When you run `gh aw compile`, it takes your `.md` workflow definition and produces a `.lock.yml` file — a compiled GitHub Actions YAML. The presence of `.lock.yml` in `.github/workflows/` is the **definitive signal** that a repo is using GitHub Agentic Workflows.

This filters out false positives from repos that just have markdown docs or unrelated YAML in their workflows directory.

## Search Queries Used

### GitHub Code Search (primary method)

```
# Query 1: 812 results
path:.github/workflows/ extension:lock.yml "agentic" OR "copilot" OR "engine"

# Query 2: 296 results  
path:.github/workflows extension:lock.yml "gh-aw" OR "agentic-workflow"

# Query 3: 412 results (for .md source files)
path:.github/workflows "engine: copilot" language:markdown
```

After deduplication by repo: **120 unique repositories** with **188 workflow files**.

### GitHub Repository Search (supplemental)

```
"agentic workflows" copilot github → 31 repos
topic:agentic-workflows topic:github-actions → 1 repo
```

## Activity Verification

For each top repo, we queried the GitHub Actions API:

```
GET /repos/{owner}/{repo}/actions/runs
```

Then filtered for runs where `path` matches `*.lock.yml` to confirm recent agentic workflow activity. This verified:

- **11 repos actively running** with recent successful runs
- **2 repos degraded** (mostly skipped or action_required)
- **2 repos failing** (100% failure rate)
- **105 repos unverified** (awaiting health-check workflow)

## Workflow Definition Reading

For 40+ workflows across the top repos, we read the actual `.md` source files:

```
GET /repos/{owner}/{repo}/contents/.github/workflows/{name}.md
```

And extracted structured data: triggers, engine, model, tools, safe-outputs, imports, pre-steps, prompt structure, and key patterns.

## Repos by Organization

| Org | Repos | Workflows | Notable |
|-----|-------|-----------|---------|
| **github** | 24 | 49 | gh-aw (23), copilot-sre, orca, blog-agent-factory, security-reviews |
| **microsoft** | 6 | 8 | wassette (3), FluidFramework, pxt-arcade, Web-Dev-For-Beginners |
| **TeamFlint-Dev** | 1 | 7 | vibe-coding-cn |
| **devantler-tech** | 2 | 5 | ksail (4), monorepo |
| **kbwaz** | 1 | 5 | rust-axum-workflows (all failing) |
| **Olino3** | 1 | 4 | forge (shared imports pattern) |
| **pelikhan** | 1 | 4 | github-agentic-workflows (demo) |
| **githubnext** | 3 | 4 | agentics (official samples) |
| **az9713** | 1 | 3 | gh-aw fork (MCP inspector) |
| **appwrite** | 1 | 1 | 44K⭐ — daily batch issue triage |
| **Kong** | 1 | 1 | kongctl — issue triage |
| **apolloconfig** | 1 | 1 | apollo (29K⭐) — issue triage |
| **JanDeDobbeleer** | 1 | 1 | oh-my-posh — workflow doctor |
| **ohcnetwork** | 1 | 1 | care_fe — daily playwright improver |
| + 50 more | 50 | 50 | Various triage, daily-status, doc-updaters |

## Continuous Discovery

The [discover-workflows](.github/workflows/discover-workflows.md) agentic workflow runs weekly to find new repos. The [health-check](.github/workflows/health-check.md) workflow runs monthly to validate existing entries.

See [data/registry.json](data/registry.json) for the complete machine-readable catalog.
