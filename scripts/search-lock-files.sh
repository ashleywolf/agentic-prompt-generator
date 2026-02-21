#!/usr/bin/env bash
# Pre-step script for discover-workflows.md
# Searches GitHub for .lock.yml files and diffs against current registry

set -euo pipefail

mkdir -p /tmp/discovery

# Copy current registry for comparison
if [ -f "$GITHUB_WORKSPACE/data/registry.json" ]; then
  cp "$GITHUB_WORKSPACE/data/registry.json" /tmp/discovery/registry-current.json
else
  echo '{"repos":{}}' > /tmp/discovery/registry-current.json
fi

# Search for .lock.yml files (the fingerprint of gh aw compile)
# Uses GitHub REST API with search endpoint
QUERY='path:.github/workflows/+extension:lock.yml+"agentic"+OR+"copilot"+OR+"engine"'

curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/code?q=${QUERY}&per_page=100" \
  > /tmp/discovery/search-results-1.json

sleep 2

QUERY2='path:.github/workflows+extension:lock.yml+"gh-aw"+OR+"agentic-workflow"'
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/search/code?q=${QUERY2}&per_page=100" \
  > /tmp/discovery/search-results-2.json

# Extract unique repos from search results
python3 - << 'PYEOF'
import json

repos = {}
for f in ["/tmp/discovery/search-results-1.json", "/tmp/discovery/search-results-2.json"]:
    with open(f) as fh:
        data = json.load(fh)
    for item in data.get("items", []):
        repo = item["repository"]
        name = repo["full_name"]
        if name not in repos:
            repos[name] = {
                "url": repo["html_url"],
                "stars": repo.get("stargazers_count", 0),
                "description": (repo.get("description") or "")[:200],
                "lock_files": []
            }
        wf = item["name"]
        if wf not in repos[name]["lock_files"]:
            repos[name]["lock_files"].append(wf)

# Load current registry
with open("/tmp/discovery/registry-current.json") as f:
    registry = json.load(f)

existing = set(registry.get("repos", {}).keys())
new_repos = {k: v for k, v in repos.items() if k not in existing}

with open("/tmp/discovery/new-repos.json", "w") as f:
    json.dump(new_repos, f, indent=2)

print(f"Found {len(repos)} total repos, {len(new_repos)} new")
PYEOF
