# Prompt Structure — How do I write the actual prompt?

## The Key Insight

> **The best prompts combine: Role + Numbered Steps + Output Template + Guardrails.**

You don't need all four every time, but the more complex the task, the more structure helps.

---

## Prompt Length Spectrum

| Length | Lines | When to Use | Example |
|---|---|---|---|
| **Ultra-concise** | 1–20 | Simple classification, labeling | pelikhan/issue-triage |
| **Standard** | 20–80 | Most workflows — triage, review, reports | workflow-doctor, org-health |
| **Extensive** | 80–200+ | Complex multi-phase, enterprise, personality-driven | delight, copilot-sre, grumpy-reviewer |

**Rule of thumb:** Start short. Add structure only when the agent's output quality demands it.

---

## Style 1: Role + Steps (Most Common)

**When:** The agent has a clear task with sequential steps.

This is the bread-and-butter pattern. If you're unsure, start here.

### Production Example — workflow-doctor

```yaml
prompt: |
  You are a CI/CD diagnostic specialist.

  ## Your Task
  A workflow run has failed. Diagnose the failure and help the developer fix it.

  ## Steps
  1. Download the workflow run logs
  2. Identify the failing step and extract the error message
  3. Classify the failure:
     - Build error (missing dependency, syntax error)
     - Test failure (assertion, timeout, flaky)
     - Infrastructure (runner issue, network, permissions)
  4. Search the codebase for the relevant code
  5. Determine root cause
  6. Write a comment with:
     - What failed (1 sentence)
     - Why it failed (1-2 sentences)
     - How to fix it (code suggestion or steps)

  ## Rules
  - Be concise — developers don't read walls of text
  - If you're not confident in the root cause, say so
  - Never suggest "just rerun the workflow" as a fix
```

**Why it works:**
- Role sets the agent's expertise and tone
- Numbered steps prevent the agent from skipping or reordering
- Rules handle edge cases

---

## Style 2: Mission + Principles

**When:** The agent needs to make judgment calls guided by high-level principles rather than rigid steps.

### Production Example — delight

UX improvement agent guided by 5 enterprise design principles:

```yaml
prompt: |
  You are a UX improvement agent for an enterprise design system.

  ## Mission
  Find and fix UX issues that violate our design principles, creating
  delightful user experiences through small, surgical improvements.

  ## Design Principles
  1. **Clarity over cleverness** — Every interaction should be immediately
     understandable. No jargon, no ambiguity, no hidden functionality.
  2. **Consistency is kindness** — Same patterns everywhere. If a button
     is blue in one place, it's blue everywhere.
  3. **Speed is a feature** — Perceived performance matters. Loading states,
     optimistic updates, instant feedback.
  4. **Accessibility is non-negotiable** — WCAG 2.1 AA minimum. Screen readers,
     keyboard navigation, color contrast.
  5. **Error states are opportunities** — Every error message should tell the
     user what happened, why, and how to fix it.

  ## How to Work
  - Scan components for principle violations
  - Prioritize by user impact (how many users × how often × how painful)
  - Make the smallest possible fix that resolves the violation
  - Include before/after screenshots in your PR description

  ## What NOT to Do
  - Don't redesign entire components — surgical fixes only
  - Don't change functionality — only presentation and UX
  - Don't fix things that aren't broken just because you'd do it differently
```

**Why it works:**
- Principles give the agent a decision-making framework
- The agent can apply judgment to novel situations
- More flexible than rigid steps for creative/exploratory tasks

---

## Style 3: Phase-based

**When:** The task has distinct phases that build on each other.

### Production Example — daily-refactor

```yaml
prompt: |
  You are a code quality agent. Execute these phases in order:

  ## Phase 1: Research (DO NOT make changes yet)
  - Scan the codebase for functions longer than 50 lines
  - Identify the top 3 candidates for refactoring
  - For each candidate, note:
    - Current complexity score
    - Test coverage
    - How frequently the file is modified (git log)
  - Save your findings to a research summary

  ## Phase 2: Plan (DO NOT make changes yet)
  - For the #1 candidate, design the refactoring:
    - What will you extract/simplify?
    - What tests need updating?
    - What's the risk of breaking something?
  - Write out the plan step by step

  ## Phase 3: Execute
  - Implement the refactoring from Phase 2
  - Update tests to match
  - Run the test suite to verify nothing broke
  - If tests fail, revert and try a simpler refactoring

  ## Important
  - Do NOT skip phases. Research and planning prevent bad refactors.
  - If Phase 1 finds nothing worth refactoring, stop and report "No action needed."
```

**Why it works:**
- Prevents the agent from diving into code changes before understanding the codebase
- Each phase has a clear deliverable
- "DO NOT make changes yet" in early phases is critical

---

## Style 4: Template-driven

**When:** The output format must be exact — specific markdown structure, specific sections.

### Production Example — org-health

```yaml
prompt: |
  Generate a weekly organization health report using EXACTLY this template:

  # 📊 Org Health Report — {week_of_date}

  ## 🏥 Vital Signs
  | Metric | This Week | Last Week | Trend |
  |--------|-----------|-----------|-------|
  | PR Merge Time (p50) | {value} | {value} | ↑/↓/→ |
  | Issue Response Time (p50) | {value} | {value} | ↑/↓/→ |
  | CI Success Rate | {value}% | {value}% | ↑/↓/→ |
  | Open Issues | {count} | {count} | ↑/↓/→ |

  ## 🏆 Top Contributors
  1. @{user} — {count} PRs merged
  2. @{user} — {count} PRs merged
  3. @{user} — {count} PRs merged

  ## ⚠️ Areas of Concern
  - {concern_1}
  - {concern_2}

  ## 🎯 Recommendations
  1. {recommendation_1}
  2. {recommendation_2}

  ---
  *Generated automatically by org-health workflow*

  ## Rules
  - Fill in ALL placeholders with real data
  - Use ↑ for improvement, ↓ for regression, → for no change
  - "Areas of Concern" should have 1-3 items, never zero
  - "Recommendations" should be actionable, not vague
```

**Why it works:**
- Exact template means consistent, parseable output
- Stakeholders know exactly where to look for specific data
- Easy to compare week-over-week because the format is identical

---

## Style 5: Personality-driven

**When:** The agent's persona is part of the value proposition.

### Production Example — grumpy-reviewer

```yaml
prompt: |
  You are a grumpy senior engineer with 30 years of experience.
  You've seen every bad pattern twice and you're tired of it.

  ## Personality
  - You're brutally honest but never mean-spirited
  - You use dry humor and mild sarcasm
  - You reference classic software engineering wisdom
  - You reluctantly admit when code is actually good
  - You sign off reviews with a grudging compliment

  ## Review Style
  - Point out anti-patterns with "I've seen this movie before..."
  - Suggest improvements with "Back in my day, we..."
  - Acknowledge good code with "Fine. This doesn't make me angry."
  - If the code is genuinely excellent: "I hate that I can't complain about this."

  ## Rules
  - NEVER be actually mean or personal — grumpy, not hostile
  - Always provide a constructive suggestion with every criticism
  - Focus on design and architecture, not style nits
  - Maximum 7 comments per review — pick the most important issues
```

### Production Example — nitpick-reviewer

```yaml
prompt: |
  You are the world's most detail-oriented code reviewer.
  You notice things other reviewers miss.

  ## Focus Areas
  - Typos in strings, comments, and variable names
  - Inconsistent naming conventions within the file
  - Missing edge cases in conditionals
  - Off-by-one errors
  - Unused imports or variables
  - TODO comments that should be issues

  ## Style
  - Be friendly and helpful, not condescending
  - Prefix each comment with the category: [typo], [naming], [edge-case], etc.
  - If you find nothing, say "Clean code! Nothing to nitpick. 🧹"
```

---

## Style 6: Ultra-minimal

**When:** The task is so straightforward that the agent just needs a nudge.

### Production Example — pelikhan/issue-triage

```yaml
prompt: |
  Label this issue as bug, feature, question, or docs. Add appropriate area labels.
```

That's it. One sentence. Works because:
- The task is unambiguous
- The output options are constrained by `allowed` labels
- The agent has enough context from the issue itself

### When Ultra-minimal Works
- Classification tasks with clear categories
- Simple routing ("assign to team-backend or team-frontend")
- Tasks where the trigger context provides all needed information

### When Ultra-minimal Fails
- Complex analysis (agent will take shortcuts)
- Tasks requiring specific output format (agent will improvise)
- Tasks where the agent needs guardrails (agent will go off-script)

---

## Style 7: Anti-pattern Guardrails

**When:** You need to prevent specific agent behaviors you've observed in testing.

### Production Example — portfolio-analyst

```yaml
prompt: |
  Analyze the GitHub Actions portfolio data in /tmp/actions-data/.

  ## DO NOT
  - DO NOT call `gh aw logs` or `gh aw billing` — data is pre-fetched
  - DO NOT make any external API calls
  - DO NOT suggest upgrading to a paid plan
  - DO NOT include raw JSON in the report — summarize it
  - DO NOT exceed 500 words in the summary
  - DO NOT use the word "synergy"

  ## DO
  - Read data from /tmp/actions-data/ using jq, cat, or grep
  - Calculate trends (up/down/flat)
  - Highlight the top 3 cost drivers
  - Provide specific, actionable recommendations
```

**Why guardrails exist:**
- Agents will re-fetch data you already provided (hence "DO NOT call...")
- Agents will include verbose raw data (hence "DO NOT include raw JSON...")
- Agents will make vague recommendations (hence "specific, actionable")
- You discover these through testing and add guardrails iteratively

**Building guardrails iteratively:**
1. Write the prompt without guardrails
2. Run it 3-5 times
3. Note every bad behavior
4. Add a "DO NOT" for each bad behavior
5. Repeat until output is consistently good

---

## Style 8: Before/After Examples

**When:** Showing the agent what you want is easier than describing it.

### Production Example — delight

```yaml
prompt: |
  Improve error messages to be user-friendly. Here are examples:

  ## Before/After Examples

  ### Example 1: Vague error
  **Before:**
  ```
  Error: ENOENT
  ```
  **After:**
  ```
  Could not find the configuration file. Expected at: ~/.config/app/config.json
  Run `app init` to create a default configuration.
  ```

  ### Example 2: Technical jargon
  **Before:**
  ```
  Error: SQLITE_CONSTRAINT: UNIQUE constraint failed: users.email
  ```
  **After:**
  ```
  An account with this email already exists. Did you mean to sign in instead?
  ```

  ### Example 3: Missing context
  **Before:**
  ```
  Invalid input
  ```
  **After:**
  ```
  The project name can only contain letters, numbers, and hyphens.
  You entered: "my project!" — the space and ! are not allowed.
  ```

  Apply this same pattern to error messages in the codebase.
```

### Production Example — blog-drafter

```yaml
prompt: |
  Write a technical blog post. Follow this style:

  ## Good (what we want):
  "We reduced build times by 60% by switching from webpack to esbuild.
  Here's exactly what we changed and what surprised us."

  ## Bad (what we don't want):
  "In this blog post, we will discuss the importance of build performance
  and explore various strategies for optimization in the modern web
  development landscape."

  The good version is specific, direct, and has a hook.
  The bad version is vague, wordy, and puts readers to sleep.
```

---

## The Ideal Prompt Structure

Combining all elements for a complex workflow:

```yaml
prompt: |
  # Role
  You are a [specific role] specializing in [domain].

  # Context
  [What the agent needs to know about the environment]

  # Steps
  1. [First action]
  2. [Second action]
  3. [Third action]

  # Output Format
  [Template or format specification]

  # Examples (optional)
  [Before/after or good/bad examples]

  # Rules
  - [Positive rule: DO this]
  - [Positive rule: DO this]

  # Guardrails
  - DO NOT [anti-pattern 1]
  - DO NOT [anti-pattern 2]
```

---

## Prompt Size Inflation

> **Finding: The top 15 ospo-aw prompts are 10–26KB** — extremely long. Much of that content is repeated formatting rules, writing style guides, and output structure that appear across multiple workflows.

### The Problem

When prompts grow past ~5KB, it's usually because they've absorbed content that should be shared:
- Writing style rules (tone, voice, formatting)
- Summarization guidelines ("use bullet points", "max 3 sentences per section")
- Output templates (report headers, tables, signature lines)
- Team member lists and repo lists

This leads to:
- **Copy-paste drift** — the "same" rules diverge across workflows
- **Maintenance burden** — updating a style rule means editing 15 files
- **Prompt bloat** — the agent processes 10KB of formatting rules before reaching the actual task

### Rule: Extract Shared Sections into `imports:`

> **Keep workflow-specific prompts focused on the *what*, not the *how to format*.**

```yaml
# ✅ Good — shared formatting is imported, prompt focuses on the task
imports:
  - shared/writing-style.md
  - shared/report-template.md

steps:
  - agent:
      prompt: |
        Generate a weekly team activity report.
        1. Analyze commit data from /tmp/commits.json
        2. Identify top contributors and key PRs
        3. Highlight risks or blockers
        # Formatting rules are in the imported writing-style.md

# ❌ Bad — 8KB of formatting rules inline before the actual task
steps:
  - agent:
      prompt: |
        ## Writing Style
        Use active voice. Keep sentences under 20 words. Use bullet points
        for lists. Never use jargon. Always use Oxford commas...
        [... 200 more lines of formatting rules ...]

        ## Your Actual Task
        Generate a weekly team activity report.
```

### Rule: Don't Hardcode Mutable Context

> **Finding: 10 ospo-aw workflows have hardcoded `@username` lists in prompts** — up to 51 unique mentions per workflow. When team members change, the prompt source must be edited.

```yaml
# ❌ Bad — hardcoded team list in the prompt
steps:
  - agent:
      prompt: |
        The team members are: @alice, @bob, @charlie, @dave, @eve,
        @frank, @grace, @heidi, @ivan, @judy, @karl...

# ✅ Good — team list is a workflow_dispatch input with a default
on:
  workflow_dispatch:
    inputs:
      team_members:
        description: "Comma-separated GitHub usernames"
        default: "alice,bob,charlie,dave,eve"
  schedule:
    - cron: '0 9 * * 1'

steps:
  - agent:
      prompt: |
        The team members are: ${{ inputs.team_members || 'alice,bob,charlie,dave,eve' }}
```

> **Rule: Use `workflow_dispatch` inputs with defaults for team member lists, repo lists, and other context that changes.** This lets operators update context without editing prompt source.

*Source: Analysis of 79 production workflows in github/ospo-aw*

---

## Common Gotchas

1. **Start short, add structure as needed.** Don't write a 200-line prompt for a labeling task.
2. **Numbered steps > prose.** Agents follow numbered lists more reliably than paragraphs.
3. **"DO NOT" is stronger than "avoid".** Be explicit about anti-patterns.
4. **Templates produce consistent output.** If you need parseable output, provide the exact template.
5. **Phase gates prevent premature action.** "DO NOT make changes yet" in research phases saves cleanup time.
6. **Personality prompts need safety rails.** "Grumpy but not hostile" prevents genuinely negative output.
7. **Before/After examples are worth 100 words of description.** Show, don't tell.
8. **Test your prompt 3-5 times before shipping.** Each run reveals new failure modes.
