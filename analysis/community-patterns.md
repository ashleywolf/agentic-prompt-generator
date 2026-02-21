## 🌐 Community Pattern Discovery

**Community workflows:** 518 across 221 orgs
**GitHub/MS workflows:** 161 across 2 orgs

### Stratified Comparison

| Metric | Community | GitHub/MS |
|--------|-----------|-----------|
| Workflow count | 518 | 161 |
| Avg success rate | 64% | 67% |
| Pre-step adoption | 11% | 25% |
| Avg prompt lines | 111.5 | 220.7 |
| Healthy rate | 50% | 60% |

### Top 15 Community Repos (by success rate, ≥3 runs)

| Repo | Stars | Workflows | Avg Success | Notable |
|------|-------|-----------|-------------|---------|
| [appwrite/appwrite](https://github.com/appwrite/appwrite) | 54898 | 1 | 100% | structured |
| [phpstan/phpstan](https://github.com/phpstan/phpstan) | 13829 | 1 | 100% | format-spec, structured |
| [opencollective/opencollective](https://github.com/opencollective/opencollective) | 2248 | 1 | 100% | structured |
| [javaevolved/javaevolved.github.io](https://github.com/javaevolved/javaevolved.github.io) | 152 | 1 | 100% | structured |
| [centminmod/explain-openclaw](https://github.com/centminmod/explain-openclaw) | 108 | 1 | 100% | structured |
| [llm-d/llm-d-inference-sim](https://github.com/llm-d/llm-d-inference-sim) | 87 | 1 | 100% | structured |
| [doggy8088/Apptopia](https://github.com/doggy8088/Apptopia) | 75 | 1 | 100% | format-spec, structured |
| [fideus-labs/ngff-zarr](https://github.com/fideus-labs/ngff-zarr) | 66 | 1 | 100% | structured |
| [pikax/verter](https://github.com/pikax/verter) | 54 | 1 | 100% | structured |
| [copilot-community-sdk/copilot-sdk-java](https://github.com/copilot-community-sdk/copilot-sdk-java) | 39 | 1 | 100% | — |
| [chrisreddington/flight-school](https://github.com/chrisreddington/flight-school) | 24 | 1 | 100% | structured |
| [talk2MeGooseman/stream_closed_captioner_phoenix](https://github.com/talk2MeGooseman/stream_closed_captioner_phoenix) | 24 | 1 | 100% | structured, pre-steps |
| [kubestellar/docs](https://github.com/kubestellar/docs) | 23 | 1 | 100% | format-spec, structured, pre-steps |
| [github-dockyard-community/radio](https://github.com/github-dockyard-community/radio) | 5 | 1 | 100% | — |
| [llm-d/llm-d-pd-utils](https://github.com/llm-d/llm-d-pd-utils) | 5 | 1 | 100% | structured |

### Trigger Patterns: Community vs GitHub/MS

| Trigger | Community % | GitHub/MS % | Community-heavy? |
|---------|------------|------------|-----------------|
| discussion | 8% | 21% |  |
| issues | 61% | 94% |  |
| pull_request | 15% | 15% |  |
| push | 10% | 4% | ✅ |
| schedule | 54% | 71% |  |
| slash_command | 4% | 9% |  |
| workflow_dispatch | 64% | 83% |  |
| workflow_run | 4% | 1% | ✅ |

### Engine/Model Diversity

| Engine | Count | % of Community |
|--------|-------|----------------|
| unknown | 352 | 68% |
| copilot | 125 | 24% |
| claude | 29 | 6% |
| codex | 10 | 2% |
| copilot-sdk | 1 | 0% |
| "copilot" | 1 | 0% |

### Potential Novel Patterns

Patterns observed in high-performing community workflows that may not be in the pattern library:

- **Discussion handlers:** 18 healthy community workflows triggered by discussions
- **Multi-trigger workflows:** 12 healthy workflows with 4+ triggers
- **Long-form prompts:** 70 healthy workflows with 150+ line prompts