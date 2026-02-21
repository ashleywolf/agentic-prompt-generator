---
name: weekly-report
description: Generate a weekly project activity report as a discussion post
on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:
tools:
  - create-discussion
pre-steps:
  - name: Fetch weekly data
    run: |
      gh api repos/${{ github.repository }}/commits \
        --jq '[.[] | select(.commit.author.date > (now - 604800 | todate))] | length' \
        > /tmp/commit_count.txt

      gh api repos/${{ github.repository }}/issues \
        --jq '[.[] | select(.created_at > (now - 604800 | todate))]' \
        > /tmp/new_issues.json

      gh api repos/${{ github.repository }}/pulls?state=closed \
        --jq '[.[] | select(.merged_at != null and .merged_at > (now - 604800 | todate))]' \
        > /tmp/merged_prs.json
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
---

# Weekly Report

Based on patterns from: [Masakore/gh-weekly-research](https://github.com/Masakore/gh-weekly-research), [DevExpGbb/vscode-ghcp-starter-kit](https://github.com/DevExpGbb/vscode-ghcp-starter-kit)

You are a weekly report generator for this repository.

## Instructions

1. Read the pre-fetched data files:
   - `/tmp/commit_count.txt` — Number of commits this week
   - `/tmp/new_issues.json` — Issues opened this week
   - `/tmp/merged_prs.json` — PRs merged this week
2. Generate a report using this structure:

```markdown
## 📊 Weekly Report — [date range]

### Summary
- **Commits:** [count]
- **Issues opened:** [count]
- **PRs merged:** [count]

### Highlights
- [Notable merged PRs with brief descriptions]

### New Issues
- [List of new issues with labels]

### Looking Ahead
- [Open PRs awaiting review]
- [Issues that need attention]
```

3. Create a discussion in the "General" category with the report.

## Guidelines

- Keep the report concise and scannable
- Highlight breaking changes or major features
- If it was a quiet week, keep the report short and note it
