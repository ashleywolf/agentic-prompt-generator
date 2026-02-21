## 📊 Success Predictors: What Configuration Matters?

**Full dataset:** 639 workflows with run data + source
**Deduplicated:** 514 unique prompts (template clones removed)

### Binary Feature Impact on Success Rate

| Feature | With (n) | Without (n) | Δ | p-value | Confidence | Dedup Δ |
|---------|----------|-------------|---|---------|------------|---------|
| Pre-fetch steps | 62% (94) | 65% (545) | -3% | 0.503 | ⚪ Weak | -2% |
| Numbered instructions | 64% (545) | 69% (94) | -5% | 0.410 | ⚪ Weak | -4% |
| Code block examples | 65% (346) | 64% (293) | +1% | 0.981 | ⚪ Weak | +5% |
| Output format spec | 63% (294) | 66% (345) | -2% | 0.238 | ⚪ Weak | +3% |
| Rate limit awareness | 74% (50) | 64% (589) | +11% | 0.059 | ⚪ Weak | +1% |
| Error handling | 62% (204) | 65% (435) | -3% | 0.251 | ⚪ Weak | +0% |
| Negative constraints (DO NOT) | 67% (230) | 63% (409) | +4% | 0.334 | ⚪ Weak | +4% |
| Bash tool enabled | 64% (103) | 65% (536) | -1% | 0.160 | ⚪ Weak | +1% |

### Success Rate by Repo Maturity

| Maturity | Avg Success | Count | Dedup Count |
|----------|-------------|-------|-------------|
| production | 64% | 184 | 164 |
| hobby | 65% | 305 | 243 |
| test | 64% | 150 | 107 |

### Numeric Feature Correlations with Success Rate

| Feature | Correlation (r) | Direction | n |
|---------|----------------|-----------|---|
| Prompt length (lines) | 0.086 | ➡️ | 639 |
| Word count | 0.057 | ➡️ | 639 |
| Section count (headings) | 0.069 | ➡️ | 639 |
| Code block count | 0.089 | ➡️ | 639 |
| Numbered steps | -0.019 | ➡️ | 639 |
| Trigger count | -0.001 | ➡️ | 639 |
| Avg sentence length | 0.128 | 📈 | 639 |

### Success Rate by Prompt Length

| Length Bucket | Avg Success | Count | Health Distribution |
|--------------|-------------|-------|---------------------|
| Short (<30 lines) | 65% | 150 | healthy: 83, failing: 46, degraded: 21 |
| Medium (30-80 lines) | 60% | 135 | healthy: 62, failing: 43, degraded: 30 |
| Long (80-150 lines) | 60% | 140 | healthy: 66, failing: 49, degraded: 25 |
| Very long (150+ lines) | 70% | 214 | healthy: 136, failing: 50, degraded: 28 |

### Success Rate by Engine

| Engine | Avg Success | Count |
|--------|-------------|-------|
| default/unknown | 67% | 352 |
| claude | 64% | 59 |
| copilot | 62% | 202 |
| codex | 47% | 22 |

### Success Rate by Trigger Combination

| Trigger Combo | Avg Success | Count |
|---------------|-------------|-------|
| issues + schedule + workflow_dispatch | 75% | 202 |
| schedule + workflow_dispatch | 80% | 76 |
| issues + workflow_dispatch | 62% | 39 |
| issues | 57% | 38 |
| issues + schedule | 73% | 30 |
| pull_request | 51% | 29 |
| discussion + issues + schedule + workflow_dispatch | 79% | 24 |
| issues + pull_request + workflow_dispatch | 51% | 15 |
| push + workflow_dispatch | 75% | 14 |
| issues + pull_request | 58% | 13 |
| discussion + issues | 79% | 12 |
| issues + pull_request + schedule + workflow_dispatch | 49% | 12 |
| workflow_run | 13% | 11 |
| workflow_dispatch | 97% | 10 |
| discussion + schedule + workflow_dispatch | 56% | 9 |

### Key Takeaways

⚠️ No features reached statistical significance at p < 0.05 — findings are directional only.

**Directional only (not significant):**

- Rate limit awareness: +11% (n=50 vs 589)
- Numbered instructions: -5% (n=545 vs 94)
- Negative constraints (DO NOT): +4% (n=230 vs 409)