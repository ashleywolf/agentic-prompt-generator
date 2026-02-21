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

### ⚖️ Bimodal Outcome Analysis

Success rate distribution is **bimodal** — most workflows either always work or always fail:

- Always succeed (100%): 245 (38%)
- Always fail (0%): 133 (21%)
- Mixed (1-99%): 261 (41%)

**Binary outcome: healthy (≥80% success) vs unhealthy**

| Feature | Healthy % (with) | Healthy % (without) | Odds Ratio | p-value |
|---------|------------------|---------------------|------------|---------|
| Pre-fetch steps | 55% (92) | 54% (422) | 1.05 | 0.838 |
| Numbered instructions | 54% (435) | 56% (79) | 0.95 | 0.813 |
| Code block examples | 56% (297) | 52% (217) | 1.18 | 0.350 |
| Output format spec | 57% (254) | 52% (260) | 1.23 | 0.240 |
| Rate limit awareness | 57% (37) | 54% (477) | 1.10 | 0.772 |
| Error handling | 54% (177) | 55% (337) | 0.95 | 0.791 |
| Negative constraints (DO NOT) | 62% (196) | 50% (318) | 1.61 | 0.009 |
| Bash tool enabled | 49% (93) | 56% (421) | 0.78 | 0.283 |

### 🧮 Multivariate Logistic Regression (Deduplicated)

Controls for confounders — isolates each feature's independent effect.

| Feature | Coefficient | Odds Ratio | Std Error | z-score | p-value | Sig |
|---------|-------------|------------|-----------|---------|---------|-----|
| Trigger count | +0.033 | 1.03 | 0.033 | 0.99 | 0.322 | ⚪ |
| Prompt length (z-scored) | +0.055 | 1.06 | 0.090 | 0.61 | 0.541 | ⚪ |
| Negative constraints (DO NOT) | +0.032 | 1.03 | 0.144 | 0.23 | 0.821 | ⚪ |
| Code examples | +0.017 | 1.02 | 0.117 | 0.15 | 0.881 | ⚪ |
| Output format spec | +0.019 | 1.02 | 0.126 | 0.15 | 0.883 | ⚪ |
| Numbered instructions | +0.012 | 1.01 | 0.096 | 0.13 | 0.897 | ⚪ |
| Production repo | +0.017 | 1.02 | 0.157 | 0.11 | 0.913 | ⚪ |
| Test repo | +0.008 | 1.01 | 0.194 | 0.04 | 0.965 | ⚪ |
| Bash tool | -0.006 | 0.99 | 0.208 | -0.03 | 0.977 | ⚪ |
| Pre-fetch steps | +0.004 | 1.00 | 0.210 | 0.02 | 0.985 | ⚪ |
| Error handling | +0.002 | 1.00 | 0.151 | 0.01 | 0.989 | ⚪ |
| Rate limit awareness | +0.002 | 1.00 | 0.331 | 0.01 | 0.994 | ⚪ |

### Key Takeaways

⚠️ No features reached statistical significance at p < 0.05 — findings are directional only.

**Directional only (not significant):**

- Rate limit awareness: +11% (n=50 vs 589)
- Numbered instructions: -5% (n=545 vs 94)
- Negative constraints (DO NOT): +4% (n=230 vs 409)