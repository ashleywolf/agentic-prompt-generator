---
name: shared/formatting
description: Shared markdown formatting utilities for agentic workflows
---

# Markdown Formatting Guide

Import this file for consistent markdown formatting across workflows.

## Collapsible Details

Use for long content that should be hidden by default:

```markdown
<details>
<summary>[Click to expand title]</summary>

[content here]

</details>
```

## Code Blocks

Always specify the language for syntax highlighting:

````markdown
```json
{ "key": "value" }
```
````

## Tables

Use aligned columns for readability:

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| value    | value    | value    |
```

## Links and References

- Issues: `#123` or `owner/repo#123`
- PRs: `#456` or `owner/repo#456`
- Commits: `` `abc1234` `` or `owner/repo@abc1234`
- Users: `@username`

## Admonitions

Use blockquotes with emoji for callouts:

```markdown
> [!NOTE]
> Informational callout

> [!WARNING]
> Warning callout

> [!IMPORTANT]
> Important callout
```

## Truncation

When content exceeds reasonable length:
1. Show the first 10 items in full
2. Summarize remaining items in a collapsible section
3. Always include a total count
