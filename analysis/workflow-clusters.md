## 🔬 Workflow Clustering: Natural Archetypes

**Sample size:** 661 workflows with source

### Detected Archetypes

| Archetype | Count | % | Avg Success | Avg Prompt Lines | Pre-Steps % |
|-----------|-------|---|-------------|------------------|-------------|
| Issue Handler | 259 | 39% | 72% | 152 | 13% |
| PR Automation | 80 | 12% | 52% | 102 | 22% |
| Scheduled Task | 72 | 11% | 79% | 107 | 35% |
| Weekly Report | 54 | 8% | 67% | 108 | 4% |
| Issue Triage | 42 | 6% | 63% | 67 | 0% |
| CI Doctor | 38 | 6% | 36% | 128 | 3% |
| Discussion Handler | 36 | 5% | 80% | 324 | 11% |
| Other | 28 | 4% | 79% | 91 | 11% |
| Moderation/Review | 26 | 4% | 48% | 134 | 15% |
| Slash Command | 26 | 4% | 5% | 192 | 19% |

### Trigger Profile Clusters

| Trigger Profile | Count | Avg Success | Common Names |
|----------------|-------|-------------|--------------|
| issues + schedule + workflow_dispatch | 205 | 75% | Issue Handler(172), Weekly Report(16) |
| schedule + workflow_dispatch | 80 | 80% | Scheduled Task(53), Weekly Report(24) |
| issues | 41 | 57% | Issue Handler(20), Issue Triage(20) |
| issues + workflow_dispatch | 41 | 62% | Issue Handler(29), Issue Triage(6) |
| issues + schedule | 30 | 73% | Issue Handler(24), Weekly Report(4) |
| pull_request | 30 | 51% | PR Automation(28), Moderation/Review(2) |
| discussion + issues + schedule + workflow_dispatch | 24 | 79% | Discussion Handler(20), Weekly Report(3) |
| issues + pull_request + workflow_dispatch | 17 | 51% | PR Automation(11), Moderation/Review(5) |
| push + workflow_dispatch | 14 | 75% | Other(14) |
| workflow_run | 13 | 13% | CI Doctor(12), Other(1) |
| discussion + issues | 13 | 79% | Discussion Handler(12), Weekly Report(1) |
| issues + pull_request | 13 | 58% | PR Automation(8), Moderation/Review(4) |
| issues + pull_request + schedule + workflow_dispatch | 12 | 49% | PR Automation(11), Moderation/Review(1) |
| workflow_dispatch | 10 | 97% | Other(7), CI Doctor(2) |
| discussion + schedule + workflow_dispatch | 9 | 56% | Scheduled Task(8), Weekly Report(1) |

### Gap Analysis: Manual vs Detected

- **Manual archetypes covered:** 8/8
- **Unclassified workflows:** 28 (4%) — may contain undocumented patterns