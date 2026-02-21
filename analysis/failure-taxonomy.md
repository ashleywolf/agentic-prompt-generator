## 🔴 Failure Taxonomy: Why Workflows Break

**Total workflows with run data:** 657
**Failing (<50% success):** 193
**Degraded (50-79%):** 109
**Healthy (≥80%):** 355

### Health Distribution

| Health | Count | % |
|--------|-------|---|
| healthy | 355 | 54% |
| degraded | 109 | 17% |
| failing | 193 | 29% |
| no_data | 0 | 0% |

### Last Run Conclusion (Failing Workflows)

| Conclusion | Count | % |
|------------|-------|---|
| success | 111 | 37% |
| failure | 110 | 36% |
| skipped | 53 | 18% |
| action_required | 21 | 7% |
| cancelled | 6 | 2% |
| None | 1 | 0% |

### Configuration: Healthy vs Failing

| Dimension | Healthy (n=347) | Failing (n=292) | Δ |
|-----------|---------------|----------------|---|
| Avg prompt lines | 152.3 | 124.5 | +27.8 |
| Avg word count | 816.5 | 708.8 | +107.7 |
| Avg sections | 16.8 | 14.2 | +2.6 |
| Avg code blocks | 3.0 | 2.2 | +0.8 |
| Has pre-steps | 15% | 15% | -0% |
| Has numbered steps | 85% | 86% | -1% |
| Has examples | 54% | 54% | +0% |
| Has format spec | 45% | 47% | -2% |
| Has error handling | 30% | 34% | -4% |

### Controlled Pairs: Same Repo, Different Outcomes

Found **34 repos** with both healthy and failing workflows:

- **Canepro/pipelinehealer**: ✅ breaking-change-checker vs ❌ ci-doctor, schema-consistency-checker
- **DoriniTT/quantum-lego**: ✅ examples-review, functional-pragmatist, code-simplifier vs ❌ terminal-stylist
- **JoshGreenslade/AITraining**: ✅ prompt-engineering-coach, team-transformation-mentor, challenge-creator vs ❌ achievement-tracker
- **MH0386/doctainr**: ✅ daily-progress, daily-test-improver, daily-repo-status vs ❌ pr-fix, ci-doctor
- **Qubinode/qubinode_navigator**: ✅ blog-auditor, doc-noob-tester vs ❌ ci-doctor
- **TeamFlint-Dev/vibe-coding-cn**: ✅ design-doc-reviewer, skill-gap-finder, project-next-step vs ❌ issue-assigner, goal-planner
- **abhimehro/email-security-pipeline**: ✅ daily-perf-improver, daily-repo-status, daily-workflow-updater vs ❌ pr-fix, plan
- **abhimehro/personal-config**: ✅ discussion-task-miner, daily-backlog-burner, daily-perf-improver vs ❌ pr-fix, plan
- **arivero/agentbook**: ✅ issue-phase1-copilot, daily-research-updates, issue-routing-decision vs ❌ issue-fast-track-close
- **danielshue/obsidian-vault-copilot**: ✅ daily-repo-status vs ❌ daily-doc-updater

### Degradation Patterns

- Workflows showing degradation (early runs better than recent): **53**
- Workflows consistently failing (all runs failed): **137**

Top degrading workflows:
  - `JasonLo/jasonlo.dev/wcag-audit` — early: 100% → recent: 0%
  - `JasonLo/jasonlo.dev/doc-cleaner` — early: 100% → recent: 0%
  - `github/gh-aw/issue-triage-agent` — early: 100% → recent: 0%
  - `jramalho/test-stuff/weekly-research` — early: 100% → recent: 0%
  - `adrianmg/test-repo/issue-triage` — early: 100% → recent: 20%