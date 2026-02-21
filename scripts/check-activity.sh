#!/usr/bin/env bash
# Pre-step script for health-check.md
# Queries GitHub Actions API for each registered repo

set -euo pipefail

mkdir -p /tmp/health

REGISTRY="$GITHUB_WORKSPACE/data/registry.json"

# Extract repo list from registry
python3 -c "
import json
with open('$REGISTRY') as f:
    data = json.load(f)
repos = list(data.get('repos', {}).keys())
for r in repos:
    print(r)
" > /tmp/health/repo-list.txt

# Query Actions API for each repo
python3 - << 'PYEOF'
import json, os, time, urllib.request

token = os.environ.get("GITHUB_TOKEN", "")
results = {}

with open("/tmp/health/repo-list.txt") as f:
    repos = [line.strip() for line in f if line.strip()]

for repo in repos:
    try:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=10"
        req = urllib.request.Request(url, headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        })
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        lock_runs = [r for r in data.get("workflow_runs", [])
                     if r.get("path", "").endswith(".lock.yml")]

        results[repo] = {
            "total_runs": data.get("total_count", 0),
            "lock_yml_runs": len(lock_runs),
            "last_run": lock_runs[0]["created_at"] if lock_runs else None,
            "last_conclusion": lock_runs[0].get("conclusion") if lock_runs else None,
            "success_count": sum(1 for r in lock_runs if r.get("conclusion") == "success"),
            "failure_count": sum(1 for r in lock_runs if r.get("conclusion") == "failure"),
        }
    except Exception as e:
        results[repo] = {"error": str(e)}

    time.sleep(0.5)  # Rate limit

with open("/tmp/health/activity-results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"Checked {len(repos)} repos")
PYEOF
