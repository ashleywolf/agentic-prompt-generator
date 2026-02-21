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

From analyzing production workflow runs:

- **Issue triage is the most reliable archetype** — ~72% success rate across repos, making it the safest starting point.
- **Prompt sweet spot is 3–8 KB** — too short and the agent lacks context; too long and it loses focus.
- **Avoid `pr-fix` and `ci-doctor` templates** — both have <20% success rates in practice.
- **100% of community workflows use the default model** — no one overrides it, so neither should you.

## Self-updating

A weekly GitHub Actions scan discovers new repos, refreshes run history, and updates the dataset automatically. The site always reflects the latest community patterns.

## Files

| File | Description |
|------|-------------|
| `index.html` | The generator site |
| `patterns.json` | Extracted pattern data powering the UI |
| `scripts/scan.sh` | Scanner that discovers and analyzes agentic workflows |
| `data/scan-results.json` | Raw scan output — every repo, workflow, and run result |

## License

MIT
