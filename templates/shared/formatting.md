---
# Shared Formatting Template
# Import this in any agent workflow for consistent output formatting.
# Usage: imports: [shared/formatting.md]

name: Shared Formatting Standards
description: GFM compliance, code blocks, links, and reference formatting for all agents
---

## Output Formatting Standards

All agent-generated content MUST follow these formatting rules for GitHub-Flavored Markdown (GFM) compliance.

### GFM Compliance

GitHub-Flavored Markdown has specific rendering rules. Follow these to ensure your output displays correctly:

1. **Blank lines**: Always put a blank line before and after:
   - Headers (`## Title`)
   - Code blocks (`` ``` ``)
   - Tables
   - Lists
   - Block quotes (`>`)
   - `<details>` blocks

2. **Line breaks**: Use two trailing spaces or `<br>` for line breaks within paragraphs. A single newline is treated as a space.

3. **Nested lists**: Indent with exactly 2 spaces for unordered lists, 3 spaces for ordered lists.

4. **HTML in Markdown**: Supported HTML tags: `<details>`, `<summary>`, `<sub>`, `<sup>`, `<br>`, `<kbd>`, `<picture>`. Other HTML tags may be stripped.

### Code Block Rules

Always specify the language for syntax highlighting:

```markdown
✅ Good:
\`\`\`javascript
const x = 1;
\`\`\`

❌ Bad:
\`\`\`
const x = 1;
\`\`\`
```

Supported language identifiers (use these exact strings):
- JavaScript: `javascript` or `js`
- TypeScript: `typescript` or `ts`
- Python: `python` or `py`
- Shell/Bash: `bash` or `sh`
- JSON: `json`
- YAML: `yaml` or `yml`
- Markdown: `markdown` or `md`
- Diff: `diff`
- SQL: `sql`
- Go: `go`
- Rust: `rust`
- HTML: `html`
- CSS: `css`

For command output with no syntax highlighting, use `text` or `console`.

For diffs, use the `diff` language:
```diff
- old line
+ new line
```

### Inline Code

Use backticks for:
- File names: `` `package.json` ``
- Function names: `` `handleSubmit()` ``
- Variable names: `` `userId` ``
- CLI commands: `` `npm install` ``
- Error codes: `` `ENOENT` ``
- Short code snippets: `` `if (x > 0)` ``

Do NOT use backticks for:
- Emphasis (use **bold** or *italic*)
- General text styling
- Names of concepts ("dependency injection", not `` `dependency injection` ``)

### Link Formatting

#### GitHub Issue/PR References

Use shorthand references — GitHub auto-links them:
- Same repo: `#123` (not `[#123](url)`)
- Cross-repo: `owner/repo#123`
- Commit: `` `abc1234` `` (first 7 chars, in backticks)

#### External Links

Use descriptive text, never bare URLs or "click here":

```markdown
✅ Good:
See the [migration guide](https://example.com/docs/migration) for details.

❌ Bad:
See https://example.com/docs/migration for details.
See [click here](https://example.com/docs/migration) for details.
```

#### User Mentions

- Use `@username` to mention GitHub users
- Be deliberate with mentions — each one sends a notification
- In automated reports, consider using `@username` only in action items, not in general statistics

### Issue/PR Reference Format

When referencing issues or PRs in reports or comments, use this consistent format:

```markdown
**In-line**: Fixed in #123 by @author
**In tables**: `#123` in the ID column
**With title**: #123 (Add user authentication)
**Cross-repo**: owner/repo#456
```

### Quoting

Use block quotes for:
- Direct quotes from error messages
- Excerpts from documentation
- User-provided context

```markdown
> Error: ECONNREFUSED 127.0.0.1:5432
> at TCPConnectWrap.afterConnect [as oncomplete]
```

Do NOT use block quotes for:
- Your own commentary or notes
- Section introductions
- Warnings (use ⚠️ emoji or `> [!WARNING]` GitHub alert syntax instead)

### GitHub Alert Syntax

Use GitHub's alert syntax for important callouts:

```markdown
> [!NOTE]
> Informational note that users should be aware of.

> [!TIP]
> Helpful advice for the reader.

> [!IMPORTANT]
> Key information users need to know.

> [!WARNING]
> Potentially dangerous or destructive action.

> [!CAUTION]
> Risks or negative outcomes to be aware of.
```

### Table Best Practices

- Keep tables to ≤ 6 columns for readability
- Use consistent alignment within columns
- Truncate long strings with `…` (max 50 chars per cell)
- For tables with > 15 rows, wrap in `<details>`
- Right-align numeric columns where possible

```markdown
| Name | Count | Change |
|:-----|------:|:------:|
| Items | 42 | ↑ +10% |
```

### Special Characters

Escape these characters when they appear in content (not as formatting):
- `|` in tables: use `\|`
- `#` at line start: use `\#`
- `-` at line start: use `\-`
- Backticks in code: use double backticks ``` `` ` `` ```
