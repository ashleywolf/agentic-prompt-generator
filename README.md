# Agentic Prompt Generator

Generate production-ready GitHub Copilot agentic workflow `.md` prompts — no guesswork, just data-driven templates.

🔗 **[Try it live →](https://ashleywolf.github.io/agentic-prompt-generator)**

## How it works

1. **Answer a few questions** — pick your workflow type, triggers, and configuration options.
2. **Get a `.md` file** — the generator produces a ready-to-use agentic workflow prompt.
3. **Drop it into `.github/workflows/`** — commit, push, and your workflow runs automatically.

## Data

The generator is powered by scanning **272 public repos** running **679 real agentic workflows** in production. Every template and default is grounded in what actually works. See [DISCOVERY.md](DISCOVERY.md) for the full scanning methodology.

## Key insights

From analyzing 4,888 production workflow runs across 269 public repos:

- **Trigger configuration is the #1 predictor** — adding `workflow_dispatch` improves success by ~21 percentage points. Adding `schedule` adds ~20pp.
- **`slash_command` triggers are broken** — 0-2% success rate across all combos. Avoid until the platform stabilizes.
- **`workflow_run` chaining fails** — 16% success rate. Use pre-steps or schedule instead.
- **Issue triage is the most reliable archetype** — ~72% success rate, making it the safest starting point.
- **Prompt sweet spot is 3–8 KB** — too short and the agent lacks context; too long and it loses focus.
- **Avoid `pr-fix` and `ci-doctor` templates** — both have <20% success rates in practice.
- **100% of community workflows use the default model** — no one overrides it, so neither should you.

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
