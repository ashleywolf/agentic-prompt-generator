## 📅 Temporal Analysis: Trends Over Time

**Dataset:** 657 workflows with run history, 4888 total run records

### Monthly Success Rate Trend

| Month | Total Runs | Success Rate | New Workflows |
|-------|-----------|--------------|---------------|
| 2025-07 | 10 | 100% | 1 |
| 2025-08 | 2 | 100% | 1 |
| 2025-09 | 24 | 38% | 7 |
| 2025-10 | 45 | 42% | 5 |
| 2025-11 | 52 | 40% | 12 |
| 2025-12 | 122 | 38% | 21 |
| 2026-01 | 322 | 52% | 47 |
| 2026-02 | 4311 | 66% | 563 |

### Adoption Curve

- First observed workflow: 2025-07
- Latest month: 2026-02
- Total unique workflows tracked: 657
- Avg new workflows/month (last 3 months): 210

### Degradation Detection

Workflows where early runs succeeded but recent runs are failing:

- **Degraded** (early ≥80%, recent <50%): 14 workflows
- **Stable healthy**: 252 workflows
- **Stable failing**: 128 workflows

| Workflow | Early Success | Recent Success | Runs |
|----------|---------------|----------------|------|
| dbroeglin/dbroeglin/hve-forge/cca-doctor.md | 100% | 0% | 3 |
| github/github/gh-aw/issue-triage-agent.md | 100% | 0% | 10 |
| jramalho/jramalho/test-stuff/weekly-research.md | 100% | 0% | 10 |
| llm-d-incubation/llm-d-incubation/llm-d-async/typo-checker.md | 80% | 0% | 10 |
| Okyerema/Okyerema/.github/continuous-triage.md | 100% | 20% | 9 |
| adrianmg/adrianmg/test-repo/issue-triage.md | 100% | 20% | 10 |
| adrianmg/adrianmg/test-repo/dad-jokes.md | 100% | 20% | 10 |
| elastic/elastic/opentelemetry-collector-components/pr-review.md | 80% | 20% | 10 |
| github/github/gh-aw/ai-moderator.md | 100% | 20% | 10 |
| yuma-722/yuma-722/gh-aw-test/github-changelog-report.md | 100% | 20% | 10 |
| h2o-innovation/h2o-innovation/H2O.Agentic.Workflows/continuous-documentation.md | 100% | 33% | 6 |
| github/github/gh-aw/daily-copilot-token-report.md | 80% | 40% | 10 |
| github/github/gh-aw/dev.md | 80% | 40% | 10 |
| llm-d-incubation/llm-d-incubation/llm-d-modelservice/typo-checker.md | 80% | 40% | 10 |

### Day-of-Week Effect

| Day | Runs | Success Rate |
|-----|------|--------------|
| Mon | 714 | 63% |
| Tue | 561 | 74% |
| Wed | 713 | 56% |
| Thu | 730 | 67% |
| Fri | 1048 | 67% |
| Sat | 756 | 54% |
| Sun | 366 | 69% |

### Run Duration Analysis

| Outcome | Count | Avg Duration | Median Duration |
|---------|-------|--------------|-----------------|
| Success | 3113 | 5.9 min | 4.7 min |
| Failure | 881 | 2.8 min | 1.4 min |

Duration difference p-value (Mann-Whitney U): 0.000

### Key Temporal Findings

- Overall trend: **declining** (100% → 66% from 2025-07 to 2026-02)
- Degraded workflows: 14 (2.1% of tracked)
- Most runs occur on: Fri