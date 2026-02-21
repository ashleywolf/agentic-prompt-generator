# Model Selection — Which model should I use?

## Rule of Thumb

| Task Type | Model | Why |
|---|---|---|
| Classification / Detection | `gpt-5.1-codex-mini` | Fast, cheap, accurate for yes/no and labeling |
| Planning / Decomposition | `claude-opus-4.6` | Best at multi-step reasoning and architecture |
| Investigation / Debugging | `claude-sonnet-4.5` | Strong code analysis, good balance of depth and speed |
| Everything else | Default (Copilot) | Good enough for 90% of workflows |

**Start with the default.** Only override when you have a specific reason.

---

## Decision Flowchart

```
What does the agent do?

├── Classify, label, or detect patterns?
│   └── gpt-5.1-codex-mini (fast + cheap)
│
├── Break down features, plan milestones, decompose work?
│   └── claude-opus-4.6 (strongest reasoning)
│
├── Debug failures, investigate code, root-cause analysis?
│   └── claude-sonnet-4.5 (deep code understanding)
│
└── Everything else (triage, reports, reviews, comments)
    └── Default — don't specify a model
```

---

## Pattern 1: Default (90% of workflows)

**When:** General-purpose triage, commenting, reviewing, reporting.

Don't specify a model at all — the platform picks the best default.

```yaml
steps:
  - agent:
      prompt: |
        Review this pull request and suggest improvements.
```

**Production examples:** Most workflows in the wild — issue triage, PR review, daily reports, slash commands.

**Why default is usually right:**
- The default model improves over time without you changing anything
- Specifying a model locks you to that version
- Default is optimized for the Copilot agent runtime

---

## Pattern 2: gpt-5.1-codex-mini — Classification & Detection

**When:** The agent's job is primarily to classify, label, detect, or make binary decisions.

**Key traits:**
- ⚡ Fastest response time
- 💰 Lowest cost per token
- 🎯 Excellent at structured output (JSON, labels, scores)
- ❌ Weaker at long-form reasoning or multi-step plans

### Production Examples

**ai-moderator** — spam and content moderation:
```yaml
steps:
  - agent:
      model: gpt-5.1-codex-mini
      prompt: |
        Classify this issue as one of: [spam, off-topic, valid-bug, feature-request].
        Respond with only the classification label.
```

**forge-duplication-detector** — [Olino3/forge](https://github.com/Olino3/forge):
```yaml
steps:
  - agent:
      model: gpt-5.1-codex-mini
      prompt: |
        Compare the new issue against existing issues.
        Determine if this is a duplicate. Output JSON:
        { "is_duplicate": true/false, "similar_issue": "#number or null", "confidence": 0.0-1.0 }
```

**forge-dependency-update-sentinel** — [Olino3/forge](https://github.com/Olino3/forge):
```yaml
steps:
  - agent:
      model: gpt-5.1-codex-mini
      prompt: |
        Check if this dependency update introduces breaking changes.
        Classify as: [safe, review-needed, breaking].
```

**Cost comparison:** ~3-5x cheaper than default, ~10x cheaper than opus.

---

## Pattern 3: claude-opus-4.6 — Planning & Decomposition

**When:** The agent needs to reason about architecture, break down complex features, or plan multi-step processes.

**Key traits:**
- 🧠 Strongest multi-step reasoning
- 📐 Best at architectural decisions
- 💰 Most expensive (use sparingly)
- 🐢 Slowest response time

### Production Examples

**forge-feature-decomposer** — [Olino3/forge](https://github.com/Olino3/forge):
```yaml
steps:
  - agent:
      model: claude-opus-4.6
      prompt: |
        Decompose this feature request into implementable sub-tasks.
        For each sub-task, specify:
        1. Title and description
        2. Estimated complexity (S/M/L)
        3. Dependencies on other sub-tasks
        4. Acceptance criteria

        Create GitHub issues for each sub-task.
```

**forge-milestone-lifecycle** — [Olino3/forge](https://github.com/Olino3/forge):
```yaml
steps:
  - agent:
      model: claude-opus-4.6
      prompt: |
        Analyze the current milestone progress:
        1. Review all open issues in the milestone
        2. Identify blockers and risks
        3. Recommend re-prioritization if needed
        4. Generate a status report with timeline projections
```

**Enterprise SRE weekly SLO report:**
```yaml
steps:
  - agent:
      model: claude-opus-4.6
      prompt: |
        Analyze SLO metrics for the past week.
        Correlate error spikes with deployment events.
        Produce an executive summary with:
        - SLO compliance percentage
        - Top 3 reliability risks
        - Recommended actions with priority
```

**When NOT to use opus:**
- Simple triage or labeling (use codex-mini)
- One-off comments or reviews (use default)
- Any workflow that runs frequently (cost adds up fast)

---

## Pattern 4: claude-sonnet-4.5 — Investigation & Debugging

**When:** The agent needs to dig into code, debug failures, or investigate complex issues.

**Key traits:**
- 🔍 Strong code comprehension
- ⚖️ Good balance of depth and speed
- 💰 Mid-range cost
- 🧪 Good at reading stack traces and logs

### Production Example

**oh-my-posh/workflow-doctor** — [JanDeDobbeleer/oh-my-posh](https://github.com/JanDeDobbeleer/oh-my-posh):
```yaml
steps:
  - agent:
      model: claude-sonnet-4.5
      prompt: |
        A CI workflow has failed. Investigate:
        1. Read the workflow logs
        2. Identify the root cause
        3. Check if this is a flaky test or a real failure
        4. If real, trace the failure back to the most recent commit
        5. Suggest a fix with code diff
```

---

## Cost & Speed Tradeoffs

| Model | Relative Cost | Speed | Best For |
|---|---|---|---|
| `gpt-5.1-codex-mini` | $ | ⚡⚡⚡ | Classification, labeling, detection |
| Default (Copilot) | $$ | ⚡⚡ | General-purpose (90% of workflows) |
| `claude-sonnet-4.5` | $$$ | ⚡⚡ | Investigation, debugging, code analysis |
| `claude-opus-4.6` | $$$$ | ⚡ | Planning, decomposition, architecture |

### Cost Optimization Tips

1. **Use codex-mini for high-frequency workflows.** A triage workflow that runs 50x/day at opus pricing will bankrupt your budget.
2. **Use opus only for low-frequency, high-value tasks.** Weekly planning, milestone reviews, architectural decomposition.
3. **Don't specify a model unless you have a reason.** Default is free from version lock-in and improves automatically.
4. **Consider a hybrid approach.** Use codex-mini for classification in step 1, then default for the response in step 2.

### Hybrid Example

```yaml
steps:
  # Step 1: Fast classification
  - agent:
      model: gpt-5.1-codex-mini
      prompt: |
        Classify this issue: [bug, feature, question, spam].
        Output only the label.

  # Step 2: Detailed response (only if not spam)
  - agent:
      prompt: |
        Based on the classification, provide a helpful response to the issue author.
```

---

## Real-World Model Usage: Production Analysis

> **Finding: 72 out of 79 production workflows use the default model**, even for complex 15–26KB prompts. Only 7 use `claude-opus-4.5`.

This reveals a common mismatch — many workflows that would benefit from a stronger model are running on default because nobody explicitly chose a model.

### The Mismatch Rule

| Signal | Right Model | Why |
|---|---|---|
| Simple triage, labeling, routing | Default (or codex-mini) | Classification doesn't need deep reasoning |
| Complex reasoning + large prompt (>8KB) + narrative writing | `claude-opus-4.6` | Large prompts need stronger attention; narrative quality scales with model |
| Sentiment analysis with nuance | `claude-opus-4.6` | Tone and nuance detection is weak in smaller models |
| Data analysis with pre-fetched data | Default | The pre-step did the hard work; agent just summarizes |

### How to Audit Your Model Choice

Ask these questions:
1. **Is the prompt over 8KB?** If yes, consider opus — smaller models lose coherence on very long prompts.
2. **Does the output require nuanced writing?** Weekly narratives, sentiment reports, and executive summaries benefit from opus.
3. **Is the workflow high-frequency?** If it runs 10+ times/day, the cost of opus adds up — stick with default or codex-mini.
4. **Is the task mechanical?** Labeling, routing, and classification don't improve with opus.

*Source: Analysis of 79 production workflows*

---

## Quick Reference

```
Is the task classification or labeling?     → gpt-5.1-codex-mini
Is the task planning or decomposition?      → claude-opus-4.6
Is the task debugging or investigation?     → claude-sonnet-4.5
Is the task anything else?                  → Don't specify (use default)
Does the workflow run 10+ times per day?    → Avoid opus, prefer codex-mini
Is the prompt >8KB with narrative output?   → Consider opus
```
