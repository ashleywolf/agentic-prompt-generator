# Agentic Prompt Generator

Generate production-ready GitHub Copilot agentic workflow `.md` prompts — no guesswork, just data-driven templates.

🔗 **[Try it live →](https://ashleywolf.github.io/agentic-prompt-generator)**

## How it works

1. **Answer a few questions** — pick your workflow type, triggers, and configuration options.
2. **Get a `.md` file** — the generator produces a ready-to-use agentic workflow prompt.
3. **Drop it into `.github/workflows/`** — commit, push, and your workflow runs automatically.

## Data

The generator is powered by scanning **269 public repos** running **679 real agentic workflows** (514 unique after template deduplication). Every template and default is grounded in what actually works — validated with statistical significance testing, not just raw averages. See [DISCOVERY.md](DISCOVERY.md) for scanning methodology and the [research issue](https://github.com/github/ospo-aw/issues/885) for the full hardened analysis.

## Key insights

From analyzing 4,888 runs across 679 workflows (514 unique after template deduplication), statistically validated with Mann-Whitney U tests, chi-squared, and multivariate logistic regression:

### What actually predicts success

- **Trigger combination is the #1 predictor.** `schedule` + `workflow_dispatch` = 80% success. `issues` + `schedule` + `workflow_dispatch` = 75%. Adding `workflow_dispatch` alone adds ~21pp.
- **`slash_command` triggers are broken** — 0-2% success rate across all combos. Avoid until the platform stabilizes.
- **`workflow_run` chaining fails** — 13% success rate. Use pre-steps or schedule instead.
- **DO NOT constraints help** — the only prompt feature reaching statistical significance (p=0.009, odds ratio 1.61). Workflows with explicit "DO NOT" instructions are 61% more likely to be healthy.
- **Engine matters** — default engine: 67%, Claude: 64%, Copilot: 62%, Codex: 47%.

### What doesn't predict success

- **Prompt content features have no measurable impact.** Error handling, rate limit awareness, code examples, format specs, numbered steps — none survive statistical testing (all p > 0.05). Include them for readability, not reliability.
- **Repo maturity doesn't matter** — production (64%), hobby (65%), and test (64%) repos all perform the same.

### Other findings

- **Success rates are bimodal** — 38% of workflows always succeed, 21% always fail, 41% are mixed. The "64% average" hides this.
- **Failures crash early** — failed runs are 2× shorter than successes (median 1.4 min vs 4.7 min, p<0.001).
- **2.1% of workflows degrade over time** — 14 workflows that started healthy are now failing.
- **Avoid `pr-fix` and `ci-doctor` templates** — both have <20% success rates in practice.
- **32% of workflows are template clones** — 179 copies of ~15 starter templates. Adapt, don't just copy.

## Self-updating

A weekly GitHub Actions scan discovers new repos, refreshes run history, and updates the dataset automatically. The site always reflects the latest community patterns.

## Deep research agent

A [deep research agent](.github/workflows/deep-research.md) runs weekly after the scan. It:

1. **Analyzes** `data/scan-results.json` — computes trigger combo success rates, archetype health, engine performance, feature correlations, and degradation trends
2. **Fetches logs** from failed workflow runs to categorize errors (timeout, rate limits, auth, crash)
3. **Compares** findings against current `patterns.json` to detect meaningful drift
4. **Opens a PR** with proposed `patterns.json` updates when the data supports changes

Run it manually:
```bash
# Local analysis (no log fetching)
python3 scripts/analyze.py --skip-logs

# Full analysis with logs
python3 scripts/analyze.py --max-log-repos 50
```

The analysis output goes to `data/analysis-report.json`.

## Files

| File | Description |
|------|-------------|
| `index.html` | The generator site |
| `patterns.json` | Extracted pattern data powering the UI |
| `scripts/scan.sh` | Scanner that discovers and analyzes agentic workflows |
| `scripts/analyze.py` | Statistical analysis — trigger combos, failure categorization, trend detection |
| `data/scan-results.json` | Raw scan output — every repo, workflow, and run result |
| `data/analysis-report.json` | Latest deep research analysis output |
| `.github/workflows/deep-research.md` | Agentic workflow that interprets analysis and opens PRs |

## License

MIT
