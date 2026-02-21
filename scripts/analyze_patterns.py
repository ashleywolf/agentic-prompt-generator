#!/usr/bin/env python3
"""
Agentic Workflow Pattern Analysis

Enriches scan-results.json with prompt source features, then runs
5 analysis workstreams:
  1. Feature extraction from prompt sources
  2. Success predictors (statistical)
  3. Workflow clustering
  4. Failure taxonomy
  5. Community pattern discovery

Usage:
    # Full pipeline (fetch sources + analyze)
    python scripts/analyze_patterns.py

    # Skip fetching (use cached sources)
    python scripts/analyze_patterns.py --skip-fetch

    # Only enrich, don't analyze
    python scripts/analyze_patterns.py --enrich-only

    # Only analyze (requires enriched-registry.json)
    python scripts/analyze_patterns.py --analyze-only
"""

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

API_DELAY = 0.3
MIN_N = 20  # minimum sample size for reported comparisons
GH_AFFILIATED = {
    "github", "githubnext", "microsoft", "Azure", "azure",
    "dotnet", "MicrosoftDocs", "microsoftgraph", "OfficeDev",
}

# ──────────────────────────────────────────────────────────────
# Source fetching
# ──────────────────────────────────────────────────────────────

def fetch_source(owner, repo, path, cache_dir):
    """Fetch .md workflow source, caching locally."""
    safe_name = f"{owner}__{repo}__{path.replace('/', '__')}"
    cache_path = Path(cache_dir) / safe_name
    if cache_path.exists():
        return cache_path.read_text(errors="replace")

    token = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/.github/workflows/{path}"
    headers = ["-H", f"Authorization: token {token}"] if token else []
    try:
        result = subprocess.run(
            ["curl", "-sL", "--max-time", "10"] + headers + [url],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout and not result.stdout.startswith("404"):
            cache_path.write_text(result.stdout)
            return result.stdout
    except Exception:
        pass
    return None


def parse_frontmatter(content):
    """Extract YAML-ish frontmatter from .md file."""
    if not content or not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()
    # Lightweight YAML parse (no PyYAML dependency)
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line and not line.startswith("-") and not line.startswith("#"):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val:
                fm[key] = val
    # Parse engine block: handle `engine: { id: copilot, model: X }`
    # and multi-line engine declarations
    engine_match = re.search(
        r'engine:\s*\{([^}]+)\}', fm_text, re.DOTALL
    )
    if engine_match:
        block = engine_match.group(1)
        for kv in block.split(","):
            kv = kv.strip()
            if ":" in kv:
                k, _, v = kv.partition(":")
                k, v = k.strip(), v.strip()
                if k == "id":
                    fm["engine_id"] = v
                elif k == "model":
                    fm["engine_model"] = v
    # Also handle multi-line:
    #   engine:
    #     id: copilot
    #     model: claude-opus-4.5
    if "engine_id" not in fm:
        lines = fm_text.split("\n")
        in_engine = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("engine:") and not stripped.replace("engine:", "").strip():
                in_engine = True
                continue
            if in_engine and stripped.startswith("id:"):
                fm["engine_id"] = stripped.split(":", 1)[1].strip()
            elif in_engine and stripped.startswith("model:"):
                fm["engine_model"] = stripped.split(":", 1)[1].strip()
            elif in_engine and not stripped.startswith("-") and ":" in stripped and not line.startswith(" "):
                in_engine = False
    return fm, body


def extract_features(content, fm, body):
    """Extract structural features from a workflow .md source."""
    lines = body.split("\n") if body else []
    words = body.split() if body else []
    sentences = re.split(r'[.!?]+', body) if body else []
    sentences = [s for s in sentences if s.strip()]

    code_blocks = re.findall(r'```[\s\S]*?```', body) if body else []
    headings = [l for l in lines if l.strip().startswith("#")]
    h2_count = sum(1 for h in headings if h.strip().startswith("## ") and not h.strip().startswith("### "))
    h3_count = sum(1 for h in headings if h.strip().startswith("### "))

    numbered_steps = sum(1 for l in lines if re.match(r'^\s*\d+[.)]\s', l))

    body_lower = body.lower() if body else ""

    return {
        "prompt_lines": len(lines),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_len": round(len(words) / max(len(sentences), 1), 1),
        "section_count": len(headings),
        "h2_count": h2_count,
        "h3_count": h3_count,
        "has_numbered_steps": numbered_steps > 0,
        "numbered_step_count": numbered_steps,
        "has_examples": len(code_blocks) > 0,
        "code_block_count": len(code_blocks),
        "has_format_spec": any(
            kw in body_lower for kw in [
                "#### format", "### format", "output format",
                "```markdown", "```json", "respond with",
            ]
        ),
        # Tightened: require instructional context, not just any mention
        "has_rate_limit_awareness": bool(re.search(
            r'(rate.?limit|pagina\w+|per_page|api.?delay|between.+calls|sequential.+search|add.+delay|wait.+between|sleep\s+\d)',
            body_lower
        )) if body else False,
        # Tightened: require action-oriented error handling, not just mentions
        "has_error_handling": bool(re.search(
            r'(if.{0,20}(fail|error|empty|no results|not found)|fallback.{0,15}(to|strategy)|retry.{0,10}(if|when|on)|handle.{0,10}(error|failure)|gracefully)',
            body_lower
        )) if body else False,
        "has_do_not_instructions": bool(re.search(
            r'(do not|don\'t|must not|never|avoid)\s+(use|search|query|call|make|create|generate|modify|delete|include)',
            body_lower
        )) if body else False,
        "mentions_safe_outputs": "safe-output" in body_lower or "safe_output" in body_lower,
        # Frontmatter-derived
        "timeout_minutes": _parse_int(fm.get("timeout-minutes", fm.get("timeout_minutes"))),
        "uses_bash": "bash" in content[:500].lower() if content else False,
        # Engine (from improved parser)
        "parsed_engine": fm.get("engine_id", fm.get("engine", "")).strip() or None,
        "parsed_model": fm.get("engine_model", fm.get("model", "")).strip() or None,
    }


def _parse_int(val):
    if val is None:
        return None
    try:
        return int(str(val).strip())
    except ValueError:
        return None


def parse_success_rate(sr_str):
    """Parse 'X/Y' fraction string to float."""
    if not sr_str:
        return None
    parts = str(sr_str).split("/")
    if len(parts) != 2:
        return None
    try:
        num, den = int(parts[0]), int(parts[1])
        return num / den if den > 0 else None
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────────
# Enrichment pipeline
# ──────────────────────────────────────────────────────────────

def enrich(scan_data, cache_dir, skip_fetch=False):
    """Enrich all workflows with source-derived features."""
    repos = scan_data["repos"]
    total = sum(len(r.get("workflows", [])) for r in repos.values())
    enriched = []
    fetched = 0
    cached = 0

    for repo_key, repo in repos.items():
        owner, repo_name = repo_key.split("/", 1) if "/" in repo_key else ("", repo_key)
        org_group = "github-ms" if owner in GH_AFFILIATED else "community"

        for wf in repo.get("workflows", []):
            record = {
                "repo": repo_key,
                "repo_url": repo.get("url", ""),
                "stars": repo.get("stars", 0),
                "repo_description": repo.get("description", ""),
                "org_group": org_group,
                "owner": owner,
                # Workflow metadata
                "name": wf.get("name", ""),
                "file": wf.get("file", ""),
                "engine": wf.get("engine", "unknown"),
                "model": wf.get("model", ""),
                "triggers": wf.get("triggers", []),
                "trigger_count": len(wf.get("triggers", [])),
                "has_pre_steps": wf.get("has_pre_steps", False),
                "safe_outputs": wf.get("safe_outputs", []),
                "safe_output_count": len(wf.get("safe_outputs", [])),
                "imports": wf.get("imports", []),
                "tools": wf.get("tools", []),
                "stop_after": wf.get("stop_after"),
                # Run history
                "success_rate_raw": wf.get("success_rate", "0/0"),
                "success_rate": parse_success_rate(wf.get("success_rate")),
                "last_conclusion": wf.get("last_conclusion"),
                "recent_runs": wf.get("recent_runs_detail", []),
                "run_count": len(wf.get("recent_runs_detail", [])),
            }

            # Classify health
            sr = record["success_rate"]
            if sr is None:
                record["health"] = "no_data"
            elif sr >= 0.8:
                record["health"] = "healthy"
            elif sr >= 0.5:
                record["health"] = "degraded"
            else:
                record["health"] = "failing"

            # Fetch source and extract features
            source = None
            if not skip_fetch and wf.get("source_available", False):
                md_file = wf["file"]
                cache_file = Path(cache_dir) / f"{owner}__{repo_name}__{md_file}"
                if cache_file.exists():
                    source = cache_file.read_text(errors="replace")
                    cached += 1
                else:
                    source = fetch_source(owner, repo_name, md_file, cache_dir)
                    if source:
                        fetched += 1
                    time.sleep(API_DELAY)

            if source:
                fm, body = parse_frontmatter(source)
                features = extract_features(source, fm, body)
                record.update(features)
                record["source_fetched"] = True
                # Template dedup: hash the prompt body
                record["prompt_hash"] = hashlib.md5(body.encode()).hexdigest()[:12] if body else None
                # Override engine/model with parsed values if available
                if features.get("parsed_engine"):
                    record["engine"] = features["parsed_engine"]
                if features.get("parsed_model"):
                    record["model"] = features["parsed_model"]
            else:
                record["source_fetched"] = False
                record["prompt_hash"] = None

            # Repo maturity classification
            stars = record["stars"]
            has_desc = bool(record.get("repo_description"))
            if stars >= 100:
                record["repo_maturity"] = "production"
            elif stars >= 5 or has_desc:
                record["repo_maturity"] = "hobby"
            else:
                record["repo_maturity"] = "test"

            enriched.append(record)

            done = len(enriched)
            if done % 50 == 0:
                print(f"  {done}/{total} workflows processed ({fetched} fetched, {cached} cached)")

    print(f"✅ Enriched {len(enriched)} workflows ({fetched} fetched, {cached} cached)")

    # Template dedup: cluster by prompt hash
    hash_groups = defaultdict(list)
    for w in enriched:
        h = w.get("prompt_hash")
        if h:
            hash_groups[h].append(w)

    # Assign template cluster IDs
    cluster_id = 0
    template_map = {}  # hash -> cluster_id
    for h, members in hash_groups.items():
        if len(members) >= 2:
            template_map[h] = f"template-{cluster_id}"
            cluster_id += 1
        else:
            template_map[h] = None

    for w in enriched:
        h = w.get("prompt_hash")
        w["template_cluster"] = template_map.get(h)
        w["is_template_clone"] = template_map.get(h) is not None

    clone_count = sum(1 for w in enriched if w["is_template_clone"])
    unique_templates = sum(1 for v in template_map.values() if v is not None)
    print(f"📋 Template dedup: {clone_count} clones in {unique_templates} template families, {len(enriched)-clone_count} unique")

    # Repo maturity distribution
    maturity = Counter(w.get("repo_maturity", "unknown") for w in enriched)
    print(f"🏗️  Repo maturity: {dict(maturity)}")

    return enriched


# ──────────────────────────────────────────────────────────────
# Analysis 1: Success Predictors
# ──────────────────────────────────────────────────────────────

def analyze_success_predictors(workflows):
    """Statistical analysis of what predicts workflow success."""
    # Filter to workflows with success data and source
    with_data = [w for w in workflows if w["success_rate"] is not None and w.get("source_fetched")]
    # Also create deduplicated set (one per template cluster)
    seen_hashes = set()
    deduped = []
    for w in with_data:
        h = w.get("prompt_hash")
        if h and h in seen_hashes:
            continue
        if h:
            seen_hashes.add(h)
        deduped.append(w)

    if len(with_data) < 20:
        return "Insufficient data for success predictor analysis."

    lines = []
    lines.append("## 📊 Success Predictors: What Configuration Matters?\n")
    lines.append(f"**Full dataset:** {len(with_data)} workflows with run data + source")
    lines.append(f"**Deduplicated:** {len(deduped)} unique prompts (template clones removed)\n")

    # Binary features vs success rate
    binary_features = [
        ("has_pre_steps", "Pre-fetch steps"),
        ("has_numbered_steps", "Numbered instructions"),
        ("has_examples", "Code block examples"),
        ("has_format_spec", "Output format spec"),
        ("has_rate_limit_awareness", "Rate limit awareness"),
        ("has_error_handling", "Error handling"),
        ("has_do_not_instructions", "Negative constraints (DO NOT)"),
        ("uses_bash", "Bash tool enabled"),
    ]

    lines.append("### Binary Feature Impact on Success Rate\n")
    lines.append("| Feature | With (n) | Without (n) | Δ | p-value | Confidence | Dedup Δ |")
    lines.append("|---------|----------|-------------|---|---------|------------|---------|")

    effects = []
    for feat_key, feat_name in binary_features:
        with_feat = [w["success_rate"] for w in with_data if w.get(feat_key)]
        without_feat = [w["success_rate"] for w in with_data if not w.get(feat_key)]
        with_dedup = [w["success_rate"] for w in deduped if w.get(feat_key)]
        without_dedup = [w["success_rate"] for w in deduped if not w.get(feat_key)]

        if len(with_feat) < MIN_N or len(without_feat) < MIN_N:
            continue

        avg_with = sum(with_feat) / len(with_feat)
        avg_without = sum(without_feat) / len(without_feat)
        delta = avg_with - avg_without

        # Mann-Whitney U test
        p_val = _mann_whitney_u(with_feat, without_feat)

        # Dedup delta
        dedup_delta = None
        if len(with_dedup) >= 10 and len(without_dedup) >= 10:
            dedup_delta = sum(with_dedup)/len(with_dedup) - sum(without_dedup)/len(without_dedup)

        # Confidence level
        if p_val is not None and p_val < 0.01 and len(with_feat) >= 50:
            conf = "🟢 Strong"
        elif p_val is not None and p_val < 0.05 and len(with_feat) >= MIN_N:
            conf = "🟡 Moderate"
        else:
            conf = "⚪ Weak"

        dedup_str = f"{dedup_delta:+.0%}" if dedup_delta is not None else "—"
        p_str = f"{p_val:.3f}" if p_val is not None else "—"

        lines.append(
            f"| {feat_name} | {avg_with:.0%} ({len(with_feat)}) | "
            f"{avg_without:.0%} ({len(without_feat)}) | "
            f"{delta:+.0%} | {p_str} | {conf} | {dedup_str} |"
        )
        effects.append((feat_name, delta, len(with_feat), len(without_feat), p_val, dedup_delta))

    # Repo maturity stratification
    lines.append("\n### Success Rate by Repo Maturity\n")
    lines.append("| Maturity | Avg Success | Count | Dedup Count |")
    lines.append("|----------|-------------|-------|-------------|")
    for mat in ["production", "hobby", "test"]:
        subset = [w for w in with_data if w.get("repo_maturity") == mat]
        dedup_subset = [w for w in deduped if w.get("repo_maturity") == mat]
        if subset:
            avg = sum(w["success_rate"] for w in subset) / len(subset)
            lines.append(f"| {mat} | {avg:.0%} | {len(subset)} | {len(dedup_subset)} |")

    # Numeric feature correlations (Spearman rank approximation)
    numeric_features = [
        ("prompt_lines", "Prompt length (lines)"),
        ("word_count", "Word count"),
        ("section_count", "Section count (headings)"),
        ("code_block_count", "Code block count"),
        ("numbered_step_count", "Numbered steps"),
        ("trigger_count", "Trigger count"),
        ("avg_sentence_len", "Avg sentence length"),
    ]

    lines.append("\n### Numeric Feature Correlations with Success Rate\n")
    lines.append("| Feature | Correlation (r) | Direction | n |")
    lines.append("|---------|----------------|-----------|---|")

    for feat_key, feat_name in numeric_features:
        pairs = [(w.get(feat_key, 0), w["success_rate"]) for w in with_data if w.get(feat_key) is not None]
        if len(pairs) < 20:
            continue
        r = _pearson([p[0] for p in pairs], [p[1] for p in pairs])
        if r is None:
            continue
        direction = "📈" if r > 0.1 else "📉" if r < -0.1 else "➡️"
        lines.append(f"| {feat_name} | {r:.3f} | {direction} | {len(pairs)} |")

    # Prompt length buckets
    lines.append("\n### Success Rate by Prompt Length\n")
    buckets = [
        ("Short (<30 lines)", lambda w: w.get("prompt_lines", 0) < 30),
        ("Medium (30-80 lines)", lambda w: 30 <= w.get("prompt_lines", 0) < 80),
        ("Long (80-150 lines)", lambda w: 80 <= w.get("prompt_lines", 0) < 150),
        ("Very long (150+ lines)", lambda w: w.get("prompt_lines", 0) >= 150),
    ]
    lines.append("| Length Bucket | Avg Success | Count | Health Distribution |")
    lines.append("|--------------|-------------|-------|---------------------|")
    for label, pred in buckets:
        subset = [w for w in with_data if pred(w)]
        if not subset:
            continue
        avg_sr = sum(w["success_rate"] for w in subset) / len(subset)
        health = Counter(w["health"] for w in subset)
        health_str = ", ".join(f"{k}: {v}" for k, v in health.most_common())
        lines.append(f"| {label} | {avg_sr:.0%} | {len(subset)} | {health_str} |")

    # Engine comparison
    lines.append("\n### Success Rate by Engine\n")
    engine_groups = defaultdict(list)
    for w in with_data:
        eng = w.get("engine", "unknown")
        if eng in ("unknown", ""):
            eng = "default/unknown"
        engine_groups[eng].append(w["success_rate"])

    lines.append("| Engine | Avg Success | Count |")
    lines.append("|--------|-------------|-------|")
    for eng, rates in sorted(engine_groups.items(), key=lambda x: -sum(x[1]) / len(x[1])):
        if len(rates) < 3:
            continue
        avg = sum(rates) / len(rates)
        lines.append(f"| {eng} | {avg:.0%} | {len(rates)} |")

    # Trigger combo analysis
    lines.append("\n### Success Rate by Trigger Combination\n")
    trigger_groups = defaultdict(list)
    for w in with_data:
        key = " + ".join(sorted(w.get("triggers", []))) or "(none)"
        trigger_groups[key].append(w["success_rate"])

    lines.append("| Trigger Combo | Avg Success | Count |")
    lines.append("|---------------|-------------|-------|")
    for combo, rates in sorted(trigger_groups.items(), key=lambda x: -len(x[1]))[:15]:
        if len(rates) < 3:
            continue
        avg = sum(rates) / len(rates)
        lines.append(f"| {combo} | {avg:.0%} | {len(rates)} |")

    # Bimodal analysis: binary outcome (healthy vs not)
    lines.append("\n### ⚖️ Bimodal Outcome Analysis\n")
    always_pass = sum(1 for w in with_data if w["success_rate"] == 1.0)
    always_fail = sum(1 for w in with_data if w["success_rate"] == 0.0)
    mixed = len(with_data) - always_pass - always_fail
    lines.append(f"Success rate distribution is **bimodal** — most workflows either always work or always fail:\n")
    lines.append(f"- Always succeed (100%): {always_pass} ({always_pass/len(with_data):.0%})")
    lines.append(f"- Always fail (0%): {always_fail} ({always_fail/len(with_data):.0%})")
    lines.append(f"- Mixed (1-99%): {mixed} ({mixed/len(with_data):.0%})\n")

    # Binary outcome: healthy (>=80% success) vs not
    lines.append("**Binary outcome: healthy (≥80% success) vs unhealthy**\n")
    lines.append("| Feature | Healthy % (with) | Healthy % (without) | Odds Ratio | p-value |")
    lines.append("|---------|------------------|---------------------|------------|---------|")

    binary_features_for_or = [
        ("has_pre_steps", "Pre-fetch steps"),
        ("has_numbered_steps", "Numbered instructions"),
        ("has_examples", "Code block examples"),
        ("has_format_spec", "Output format spec"),
        ("has_rate_limit_awareness", "Rate limit awareness"),
        ("has_error_handling", "Error handling"),
        ("has_do_not_instructions", "Negative constraints (DO NOT)"),
        ("uses_bash", "Bash tool enabled"),
    ]

    for feat_key, feat_name in binary_features_for_or:
        with_feat = [w for w in deduped if w.get(feat_key)]
        without_feat = [w for w in deduped if not w.get(feat_key)]
        if len(with_feat) < MIN_N or len(without_feat) < MIN_N:
            continue
        # Healthy = success_rate >= 0.8
        a = sum(1 for w in with_feat if w["success_rate"] >= 0.8)   # with + healthy
        b = len(with_feat) - a                                       # with + unhealthy
        c = sum(1 for w in without_feat if w["success_rate"] >= 0.8) # without + healthy
        d = len(without_feat) - c                                     # without + unhealthy
        # Odds ratio (add 0.5 for zero-cell correction)
        odds_ratio = ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
        # Fisher's exact test approximation via chi-squared
        n_total = a + b + c + d
        expected_a = (a + b) * (a + c) / n_total
        expected_b = (a + b) * (b + d) / n_total
        expected_c = (c + d) * (a + c) / n_total
        expected_d = (c + d) * (b + d) / n_total
        chi2 = 0
        for obs, exp in [(a, expected_a), (b, expected_b), (c, expected_c), (d, expected_d)]:
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp
        # Chi-squared to p-value (1 df) using normal approx
        p_val = 2 * (1 - _norm_cdf(math.sqrt(chi2))) if chi2 > 0 else 1.0
        healthy_with = a / len(with_feat) if with_feat else 0
        healthy_without = c / len(without_feat) if without_feat else 0
        or_str = f"{odds_ratio:.2f}" if odds_ratio < 10 else f"{odds_ratio:.1f}"
        lines.append(f"| {feat_name} | {healthy_with:.0%} ({len(with_feat)}) | {healthy_without:.0%} ({len(without_feat)}) | {or_str} | {p_val:.3f} |")

    # Logistic regression (multivariate)
    lines.append("\n### 🧮 Multivariate Logistic Regression (Deduplicated)\n")
    lines.append("Controls for confounders — isolates each feature's independent effect.\n")

    logreg_result = _logistic_regression(deduped)
    if logreg_result:
        lines.append("| Feature | Coefficient | Odds Ratio | Std Error | z-score | p-value | Sig |")
        lines.append("|---------|-------------|------------|-----------|---------|---------|-----|")
        for name, coef, se, z, p, odds in logreg_result:
            sig = "✅" if p < 0.05 else "⚪"
            lines.append(f"| {name} | {coef:+.3f} | {odds:.2f} | {se:.3f} | {z:.2f} | {p:.3f} | {sig} |")
    else:
        lines.append("*Logistic regression could not converge with available data.*\n")

    # Top takeaways
    lines.append("\n### Key Takeaways\n")
    if effects:
        # Only report statistically significant findings
        sig_effects = [(n, d, nw, nwo, p, dd) for n, d, nw, nwo, p, dd in effects if p is not None and p < 0.05]
        if sig_effects:
            lines.append("**Statistically significant findings (p < 0.05):**\n")
            sorted_effects = sorted(sig_effects, key=lambda x: -abs(x[1]))
            for name, delta, n_with, n_without, p_val, dedup_d in sorted_effects:
                direction = "increases" if delta > 0 else "decreases"
                survives = ""
                if dedup_d is not None:
                    if (delta > 0 and dedup_d > 0) or (delta < 0 and dedup_d < 0):
                        survives = " ✅ survives dedup"
                    else:
                        survives = " ⚠️ reverses after dedup"
                lines.append(f"- **{name}** {direction} success rate by {abs(delta):.0%} (p={p_val:.3f}, n={n_with} vs {n_without}){survives}")
        else:
            lines.append("⚠️ No features reached statistical significance at p < 0.05 — findings are directional only.")

        nonsig = [(n, d, nw, nwo) for n, d, nw, nwo, p, dd in effects if p is None or p >= 0.05]
        if nonsig:
            lines.append("\n**Directional only (not significant):**\n")
            for name, delta, n_with, n_without in sorted(nonsig, key=lambda x: -abs(x[1]))[:3]:
                lines.append(f"- {name}: {delta:+.0%} (n={n_with} vs {n_without})")

    return "\n".join(lines)


def _pearson(xs, ys):
    """Simple Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def _mann_whitney_u(xs, ys):
    """Mann-Whitney U test (normal approximation for large samples).
    Returns p-value or None if samples too small."""
    nx, ny = len(xs), len(ys)
    if nx < 10 or ny < 10:
        return None

    # Rank all values
    combined = [(v, 0) for v in xs] + [(v, 1) for v in ys]
    combined.sort(key=lambda x: x[0])

    # Assign ranks (handle ties with average rank)
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-indexed average
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    # Sum ranks for group 0 (xs)
    r1 = sum(ranks[i] for i in range(len(combined)) if combined[i][1] == 0)

    u1 = r1 - nx * (nx + 1) / 2
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)

    if sigma == 0:
        return None

    z = (u1 - mu) / sigma
    # Two-tailed p-value (normal approximation)
    p = 2 * (1 - _norm_cdf(abs(z)))
    return p


def _norm_cdf(x):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x = abs(x) / math.sqrt(2)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * y)


def _logistic_regression(workflows, max_iter=100, lr=0.01):
    """Pure-Python logistic regression via gradient descent.
    Returns list of (feature_name, coefficient, std_error, z_score, p_value, odds_ratio)
    or None if can't converge."""
    feature_names = [
        "prompt_lines_z", "trigger_count", "has_pre_steps", "has_examples",
        "has_format_spec", "has_error_handling", "has_rate_limit_awareness",
        "has_do_not_instructions", "uses_bash", "has_numbered_steps",
        "is_production", "is_test",
    ]
    display_names = [
        "Prompt length (z-scored)", "Trigger count", "Pre-fetch steps", "Code examples",
        "Output format spec", "Error handling", "Rate limit awareness",
        "Negative constraints (DO NOT)", "Bash tool", "Numbered instructions",
        "Production repo", "Test repo",
    ]

    # Build feature matrix and outcome
    X = []
    y = []
    for w in workflows:
        if w.get("success_rate") is None:
            continue
        row = [
            w.get("prompt_lines", 0),   # will z-score below
            w.get("trigger_count", 1),
            1 if w.get("has_pre_steps") else 0,
            1 if w.get("has_examples") else 0,
            1 if w.get("has_format_spec") else 0,
            1 if w.get("has_error_handling") else 0,
            1 if w.get("has_rate_limit_awareness") else 0,
            1 if w.get("has_do_not_instructions") else 0,
            1 if w.get("uses_bash") else 0,
            1 if w.get("has_numbered_steps") else 0,
            1 if w.get("repo_maturity") == "production" else 0,
            1 if w.get("repo_maturity") == "test" else 0,
        ]
        X.append(row)
        y.append(1 if w["success_rate"] >= 0.8 else 0)  # binary: healthy

    if len(X) < 50:
        return None

    n_samples = len(X)
    n_features = len(feature_names)

    # Z-score prompt_lines (column 0)
    col0 = [row[0] for row in X]
    mean0 = sum(col0) / len(col0)
    std0 = math.sqrt(sum((v - mean0) ** 2 for v in col0) / len(col0))
    if std0 > 0:
        for row in X:
            row[0] = (row[0] - mean0) / std0

    # Add intercept (column 0)
    for row in X:
        row.insert(0, 1.0)
    feature_names_full = ["intercept"] + feature_names
    display_names_full = ["(Intercept)"] + display_names
    n_features_full = n_features + 1

    # Initialize weights
    w_vec = [0.0] * n_features_full

    def sigmoid(z):
        z = max(-500, min(500, z))
        return 1.0 / (1.0 + math.exp(-z))

    # Gradient descent with adaptive learning rate
    for iteration in range(max_iter):
        # Compute predictions
        preds = []
        for row in X:
            z = sum(w_vec[j] * row[j] for j in range(n_features_full))
            preds.append(sigmoid(z))

        # Compute gradient
        grad = [0.0] * n_features_full
        for i in range(n_samples):
            err = preds[i] - y[i]
            for j in range(n_features_full):
                grad[j] += err * X[i][j]

        # Update weights
        for j in range(n_features_full):
            w_vec[j] -= lr * grad[j] / n_samples

    # Compute standard errors via Hessian diagonal approximation
    preds_final = []
    for row in X:
        z = sum(w_vec[j] * row[j] for j in range(n_features_full))
        preds_final.append(sigmoid(z))

    # Diagonal of Fisher information matrix
    se = []
    for j in range(n_features_full):
        fisher_jj = sum(preds_final[i] * (1 - preds_final[i]) * X[i][j] ** 2 for i in range(n_samples))
        if fisher_jj > 1e-10:
            se.append(1.0 / math.sqrt(fisher_jj))
        else:
            se.append(float("inf"))

    results = []
    for j in range(1, n_features_full):  # skip intercept
        coef = w_vec[j]
        std_err = se[j]
        z_score = coef / std_err if std_err > 0 and std_err != float("inf") else 0
        p_value = 2 * (1 - _norm_cdf(abs(z_score)))
        odds_ratio = math.exp(min(coef, 20))  # cap to avoid overflow
        results.append((display_names[j - 1], coef, std_err, z_score, p_value, odds_ratio))

    # Sort by absolute z-score (most significant first)
    results.sort(key=lambda x: -abs(x[3]))
    return results


# ──────────────────────────────────────────────────────────────
# Temporal Analysis
# ──────────────────────────────────────────────────────────────

def analyze_temporal(workflows):
    """Time-series analysis: success trends, adoption curves, degradation detection."""
    with_runs = [w for w in workflows if w.get("recent_runs") and len(w["recent_runs"]) > 0]
    if len(with_runs) < 30:
        return "Insufficient temporal data for analysis."

    lines = []
    lines.append("## 📅 Temporal Analysis: Trends Over Time\n")
    lines.append(f"**Dataset:** {len(with_runs)} workflows with run history, "
                 f"{sum(len(w['recent_runs']) for w in with_runs)} total run records\n")

    # Collect all runs by month
    monthly_runs = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
    weekly_runs = defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
    workflow_first_run = {}
    workflow_trajectories = defaultdict(list)

    for w in with_runs:
        wf_id = f"{w['owner']}/{w['repo']}/{w['file']}"
        for run in w["recent_runs"]:
            try:
                dt = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            except (ValueError, KeyError):
                continue
            month_key = dt.strftime("%Y-%m")
            week_key = dt.strftime("%Y-W%W")
            is_success = run.get("conclusion") == "success"

            monthly_runs[month_key]["total"] += 1
            monthly_runs[month_key]["success" if is_success else "failure"] += 1
            weekly_runs[week_key]["total"] += 1
            weekly_runs[week_key]["success" if is_success else "failure"] += 1

            workflow_trajectories[wf_id].append((dt, is_success))

            if wf_id not in workflow_first_run or dt < workflow_first_run[wf_id]:
                workflow_first_run[wf_id] = dt

    # Monthly success rate trend
    lines.append("### Monthly Success Rate Trend\n")
    lines.append("| Month | Total Runs | Success Rate | New Workflows |")
    lines.append("|-------|-----------|--------------|---------------|")

    monthly_new = Counter()
    for wf_id, first_dt in workflow_first_run.items():
        monthly_new[first_dt.strftime("%Y-%m")] += 1

    for month in sorted(monthly_runs.keys()):
        data = monthly_runs[month]
        sr = data["success"] / data["total"] if data["total"] > 0 else 0
        new_wf = monthly_new.get(month, 0)
        lines.append(f"| {month} | {data['total']} | {sr:.0%} | {new_wf} |")

    # Adoption curve
    lines.append("\n### Adoption Curve\n")
    cumulative = 0
    adoption_data = []
    for month in sorted(monthly_new.keys()):
        cumulative += monthly_new[month]
        adoption_data.append((month, cumulative, monthly_new[month]))

    if len(adoption_data) > 1:
        lines.append(f"- First observed workflow: {adoption_data[0][0]}")
        lines.append(f"- Latest month: {adoption_data[-1][0]}")
        lines.append(f"- Total unique workflows tracked: {adoption_data[-1][1]}")
        recent_3 = [d for d in adoption_data if d[0] >= sorted(monthly_new.keys())[-3]]
        avg_recent = sum(d[2] for d in recent_3) / len(recent_3) if recent_3 else 0
        lines.append(f"- Avg new workflows/month (last 3 months): {avg_recent:.0f}")

    # Degradation detection: workflows that started healthy then turned unhealthy
    lines.append("\n### Degradation Detection\n")
    lines.append("Workflows where early runs succeeded but recent runs are failing:\n")

    degraded_list = []
    stable_good = 0
    stable_bad = 0

    for wf_id, trajectory in workflow_trajectories.items():
        if len(trajectory) < 3:
            continue
        trajectory.sort(key=lambda x: x[0])
        half = len(trajectory) // 2
        early = trajectory[:half]
        late = trajectory[half:]
        early_sr = sum(1 for _, s in early if s) / len(early)
        late_sr = sum(1 for _, s in late if s) / len(late)

        if early_sr >= 0.8 and late_sr < 0.5:
            degraded_list.append((wf_id, early_sr, late_sr, len(trajectory)))
        elif early_sr >= 0.8 and late_sr >= 0.8:
            stable_good += 1
        elif early_sr < 0.5 and late_sr < 0.5:
            stable_bad += 1

    lines.append(f"- **Degraded** (early ≥80%, recent <50%): {len(degraded_list)} workflows")
    lines.append(f"- **Stable healthy**: {stable_good} workflows")
    lines.append(f"- **Stable failing**: {stable_bad} workflows")

    if degraded_list:
        lines.append("\n| Workflow | Early Success | Recent Success | Runs |")
        lines.append("|----------|---------------|----------------|------|")
        for wf_id, early, late, n in sorted(degraded_list, key=lambda x: x[2])[:15]:
            lines.append(f"| {wf_id} | {early:.0%} | {late:.0%} | {n} |")

    # Day-of-week effect
    lines.append("\n### Day-of-Week Effect\n")
    dow_runs = defaultdict(lambda: {"success": 0, "total": 0})
    dow_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for w in with_runs:
        for run in w["recent_runs"]:
            try:
                dt = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
            except (ValueError, KeyError):
                continue
            dow = dt.weekday()
            dow_runs[dow]["total"] += 1
            if run.get("conclusion") == "success":
                dow_runs[dow]["success"] += 1

    lines.append("| Day | Runs | Success Rate |")
    lines.append("|-----|------|--------------|")
    for i in range(7):
        if dow_runs[i]["total"] > 0:
            sr = dow_runs[i]["success"] / dow_runs[i]["total"]
            lines.append(f"| {dow_names[i]} | {dow_runs[i]['total']} | {sr:.0%} |")

    # Run duration analysis (if available)
    durations_success = []
    durations_failure = []
    for w in with_runs:
        for run in w["recent_runs"]:
            try:
                start = datetime.fromisoformat(run["run_started_at"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
                dur_min = (end - start).total_seconds() / 60
                if 0 < dur_min < 120:  # filter outliers
                    if run.get("conclusion") == "success":
                        durations_success.append(dur_min)
                    elif run.get("conclusion") == "failure":
                        durations_failure.append(dur_min)
            except (ValueError, KeyError):
                continue

    if durations_success and durations_failure:
        lines.append("\n### Run Duration Analysis\n")
        avg_s = sum(durations_success) / len(durations_success)
        avg_f = sum(durations_failure) / len(durations_failure)
        med_s = sorted(durations_success)[len(durations_success) // 2]
        med_f = sorted(durations_failure)[len(durations_failure) // 2]
        lines.append("| Outcome | Count | Avg Duration | Median Duration |")
        lines.append("|---------|-------|--------------|-----------------|")
        lines.append(f"| Success | {len(durations_success)} | {avg_s:.1f} min | {med_s:.1f} min |")
        lines.append(f"| Failure | {len(durations_failure)} | {avg_f:.1f} min | {med_f:.1f} min |")

        p_dur = _mann_whitney_u(durations_success, durations_failure)
        if p_dur is not None:
            lines.append(f"\nDuration difference p-value (Mann-Whitney U): {p_dur:.3f}")

    # Key temporal findings
    lines.append("\n### Key Temporal Findings\n")
    if monthly_runs:
        months_sorted = sorted(monthly_runs.keys())
        if len(months_sorted) >= 2:
            first_month = monthly_runs[months_sorted[0]]
            last_month = monthly_runs[months_sorted[-1]]
            first_sr = first_month["success"] / first_month["total"] if first_month["total"] > 0 else 0
            last_sr = last_month["success"] / last_month["total"] if last_month["total"] > 0 else 0
            trend = "improving" if last_sr > first_sr + 0.05 else "declining" if last_sr < first_sr - 0.05 else "stable"
            lines.append(f"- Overall trend: **{trend}** ({first_sr:.0%} → {last_sr:.0%} from {months_sorted[0]} to {months_sorted[-1]})")
    lines.append(f"- Degraded workflows: {len(degraded_list)} ({len(degraded_list)/len(workflow_trajectories)*100:.1f}% of tracked)")
    lines.append(f"- Most runs occur on: {dow_names[max(dow_runs, key=lambda d: dow_runs[d]['total'])] if dow_runs else 'N/A'}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Analysis 2: Workflow Clustering
# ──────────────────────────────────────────────────────────────

def analyze_clustering(workflows):
    """Find natural workflow clusters and compare to manual archetypes."""
    with_source = [w for w in workflows if w.get("source_fetched")]
    if len(with_source) < 30:
        return "Insufficient data for clustering analysis."

    lines = []
    lines.append("## 🔬 Workflow Clustering: Natural Archetypes\n")
    lines.append(f"**Sample size:** {len(with_source)} workflows with source\n")

    # Manual archetype detection from triggers + safe_outputs + name patterns
    def classify_archetype(w):
        name = (w.get("name", "") + " " + w.get("file", "")).lower()
        triggers = set(w.get("triggers", []))
        safe = set(w.get("safe_outputs", []))

        if "triage" in name or ("issues" in triggers and "add-labels" in safe):
            return "Issue Triage"
        if "doctor" in name or "fix" in name or "ci" in name:
            return "CI Doctor"
        if "weekly" in name or "report" in name or "summary" in name:
            return "Weekly Report"
        if "moderat" in name or "review" in name:
            return "Moderation/Review"
        if "slash" in name or "slash_command" in triggers:
            return "Slash Command"
        if "schedule" in triggers and "issues" not in triggers:
            return "Scheduled Task"
        if "pull_request" in triggers:
            return "PR Automation"
        if "discussion" in triggers:
            return "Discussion Handler"
        if "issues" in triggers:
            return "Issue Handler"
        return "Other"

    archetype_dist = Counter()
    archetype_success = defaultdict(list)
    archetype_features = defaultdict(lambda: defaultdict(list))

    for w in with_source:
        arch = classify_archetype(w)
        archetype_dist[arch] += 1
        if w["success_rate"] is not None:
            archetype_success[arch].append(w["success_rate"])
        archetype_features[arch]["prompt_lines"].append(w.get("prompt_lines", 0))
        archetype_features[arch]["has_pre_steps"].append(1 if w.get("has_pre_steps") else 0)
        archetype_features[arch]["has_format_spec"].append(1 if w.get("has_format_spec") else 0)

    lines.append("### Detected Archetypes\n")
    lines.append("| Archetype | Count | % | Avg Success | Avg Prompt Lines | Pre-Steps % |")
    lines.append("|-----------|-------|---|-------------|------------------|-------------|")

    for arch, count in archetype_dist.most_common():
        pct = count / len(with_source)
        avg_sr = sum(archetype_success[arch]) / len(archetype_success[arch]) if archetype_success[arch] else 0
        avg_lines = sum(archetype_features[arch]["prompt_lines"]) / max(len(archetype_features[arch]["prompt_lines"]), 1)
        prestep_pct = sum(archetype_features[arch]["has_pre_steps"]) / max(len(archetype_features[arch]["has_pre_steps"]), 1)
        lines.append(
            f"| {arch} | {count} | {pct:.0%} | {avg_sr:.0%} | {avg_lines:.0f} | {prestep_pct:.0%} |"
        )

    # Feature-based clustering (simple k-means without sklearn)
    # Use trigger profile as the clustering basis
    lines.append("\n### Trigger Profile Clusters\n")
    trigger_profiles = defaultdict(list)
    for w in with_source:
        profile = tuple(sorted(w.get("triggers", [])))
        trigger_profiles[profile].append(w)

    lines.append("| Trigger Profile | Count | Avg Success | Common Names |")
    lines.append("|----------------|-------|-------------|--------------|")
    for profile, wfs in sorted(trigger_profiles.items(), key=lambda x: -len(x[1]))[:15]:
        if len(wfs) < 3:
            continue
        profile_str = " + ".join(profile) if profile else "(none)"
        rates = [w["success_rate"] for w in wfs if w["success_rate"] is not None]
        avg_sr = sum(rates) / len(rates) if rates else 0
        names = Counter(classify_archetype(w) for w in wfs).most_common(2)
        names_str = ", ".join(f"{n}({c})" for n, c in names)
        lines.append(f"| {profile_str} | {len(wfs)} | {avg_sr:.0%} | {names_str} |")

    # Gap analysis
    lines.append("\n### Gap Analysis: Manual vs Detected\n")
    manual_archetypes = {
        "Issue Triage", "CI Doctor", "Weekly Report", "Slash Command",
        "Moderation/Review", "Scheduled Task", "PR Automation", "Discussion Handler",
    }
    detected = set(archetype_dist.keys())
    novel = detected - manual_archetypes - {"Other", "Issue Handler"}
    missing = manual_archetypes - detected
    lines.append(f"- **Manual archetypes covered:** {len(detected & manual_archetypes)}/{len(manual_archetypes)}")
    if novel:
        lines.append(f"- **Novel clusters found:** {', '.join(novel)}")
    if missing:
        lines.append(f"- **Manual archetypes not found in data:** {', '.join(missing)}")
    other_count = archetype_dist.get("Other", 0)
    if other_count:
        lines.append(f"- **Unclassified workflows:** {other_count} ({other_count/len(with_source):.0%}) — may contain undocumented patterns")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Analysis 3: Failure Taxonomy
# ──────────────────────────────────────────────────────────────

def analyze_failures(workflows):
    """Classify and catalog failure modes."""
    failing = [w for w in workflows if w.get("health") in ("failing", "degraded")]
    all_with_runs = [w for w in workflows if w["success_rate"] is not None]

    lines = []
    lines.append("## 🔴 Failure Taxonomy: Why Workflows Break\n")
    lines.append(f"**Total workflows with run data:** {len(all_with_runs)}")
    lines.append(f"**Failing (<50% success):** {sum(1 for w in all_with_runs if w['health'] == 'failing')}")
    lines.append(f"**Degraded (50-79%):** {sum(1 for w in all_with_runs if w['health'] == 'degraded')}")
    lines.append(f"**Healthy (≥80%):** {sum(1 for w in all_with_runs if w['health'] == 'healthy')}\n")

    # Health distribution
    health_dist = Counter(w["health"] for w in all_with_runs)
    lines.append("### Health Distribution\n")
    lines.append("| Health | Count | % |")
    lines.append("|--------|-------|---|")
    for h in ["healthy", "degraded", "failing", "no_data"]:
        c = health_dist.get(h, 0)
        lines.append(f"| {h} | {c} | {c/len(all_with_runs):.0%} |")

    # Last conclusion breakdown for failing workflows
    lines.append("\n### Last Run Conclusion (Failing Workflows)\n")
    conclusions = Counter(w.get("last_conclusion", "unknown") for w in failing)
    lines.append("| Conclusion | Count | % |")
    lines.append("|------------|-------|---|")
    for conc, count in conclusions.most_common():
        lines.append(f"| {conc} | {count} | {count/max(len(failing),1):.0%} |")

    # Configuration comparison: failing vs healthy
    healthy = [w for w in all_with_runs if w["health"] == "healthy" and w.get("source_fetched")]
    failing_with_source = [w for w in failing if w.get("source_fetched")]

    if healthy and failing_with_source:
        lines.append("\n### Configuration: Healthy vs Failing\n")
        lines.append("| Dimension | Healthy (n={}) | Failing (n={}) | Δ |".format(len(healthy), len(failing_with_source)))
        lines.append("|-----------|---------------|----------------|---|")

        comparisons = [
            ("Avg prompt lines", "prompt_lines"),
            ("Avg word count", "word_count"),
            ("Avg sections", "section_count"),
            ("Avg code blocks", "code_block_count"),
        ]
        for label, key in comparisons:
            h_vals = [w.get(key, 0) for w in healthy]
            f_vals = [w.get(key, 0) for w in failing_with_source]
            h_avg = sum(h_vals) / len(h_vals) if h_vals else 0
            f_avg = sum(f_vals) / len(f_vals) if f_vals else 0
            delta = h_avg - f_avg
            lines.append(f"| {label} | {h_avg:.1f} | {f_avg:.1f} | {delta:+.1f} |")

        bool_comparisons = [
            ("Has pre-steps", "has_pre_steps"),
            ("Has numbered steps", "has_numbered_steps"),
            ("Has examples", "has_examples"),
            ("Has format spec", "has_format_spec"),
            ("Has error handling", "has_error_handling"),
        ]
        for label, key in bool_comparisons:
            h_pct = sum(1 for w in healthy if w.get(key)) / len(healthy)
            f_pct = sum(1 for w in failing_with_source if w.get(key)) / len(failing_with_source)
            delta = h_pct - f_pct
            lines.append(f"| {label} | {h_pct:.0%} | {f_pct:.0%} | {delta:+.0%} |")

    # Controlled pairs: repos with both healthy and failing workflows
    lines.append("\n### Controlled Pairs: Same Repo, Different Outcomes\n")
    repo_health = defaultdict(lambda: {"healthy": [], "failing": []})
    for w in all_with_runs:
        if w["health"] in ("healthy", "failing"):
            repo_health[w["repo"]][w["health"]].append(w)

    pairs = {r: h for r, h in repo_health.items() if h["healthy"] and h["failing"]}
    if pairs:
        lines.append(f"Found **{len(pairs)} repos** with both healthy and failing workflows:\n")
        for repo, health_map in sorted(pairs.items())[:10]:
            h_names = [w["name"] for w in health_map["healthy"][:3]]
            f_names = [w["name"] for w in health_map["failing"][:3]]
            lines.append(f"- **{repo}**: ✅ {', '.join(h_names)} vs ❌ {', '.join(f_names)}")
    else:
        lines.append("No repos found with both healthy and failing workflows.")

    # Survival: run history timeline for failing workflows
    lines.append("\n### Degradation Patterns\n")
    degrading = []
    for w in failing:
        runs = w.get("recent_runs", [])
        if len(runs) >= 3:
            early = runs[len(runs)//2:]  # older half
            late = runs[:len(runs)//2]   # newer half
            early_success = sum(1 for r in early if r.get("conclusion") == "success") / len(early) if early else 0
            late_success = sum(1 for r in late if r.get("conclusion") == "success") / len(late) if late else 0
            if early_success > late_success:
                degrading.append((w, early_success, late_success))

    lines.append(f"- Workflows showing degradation (early runs better than recent): **{len(degrading)}**")
    lines.append(f"- Workflows consistently failing (all runs failed): **{sum(1 for w in failing if w['success_rate'] == 0)}**")

    if degrading:
        lines.append("\nTop degrading workflows:")
        for w, early, late in sorted(degrading, key=lambda x: x[1] - x[2], reverse=True)[:5]:
            lines.append(f"  - `{w['repo']}/{w['name']}` — early: {early:.0%} → recent: {late:.0%}")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Analysis 4: Community Patterns
# ──────────────────────────────────────────────────────────────

def analyze_community(workflows):
    """Discover novel patterns from community repos."""
    community = [w for w in workflows if w["org_group"] == "community"]
    ghms = [w for w in workflows if w["org_group"] == "github-ms"]

    lines = []
    lines.append("## 🌐 Community Pattern Discovery\n")
    lines.append(f"**Community workflows:** {len(community)} across {len(set(w['owner'] for w in community))} orgs")
    lines.append(f"**GitHub/MS workflows:** {len(ghms)} across {len(set(w['owner'] for w in ghms))} orgs\n")

    # Stratified comparison
    lines.append("### Stratified Comparison\n")
    lines.append("| Metric | Community | GitHub/MS |")
    lines.append("|--------|-----------|-----------|")

    for label, group in [("Community", community), ("GitHub/MS", ghms)]:
        pass  # Build comparison below

    metrics = {}
    for label, group in [("Community", community), ("GitHub/MS", ghms)]:
        if not group:
            metrics[label] = {}
            continue
        rates = [w["success_rate"] for w in group if w["success_rate"] is not None]
        metrics[label] = {
            "count": len(group),
            "avg_success": sum(rates) / len(rates) if rates else 0,
            "has_pre_steps": sum(1 for w in group if w.get("has_pre_steps")) / len(group),
            "avg_prompt_lines": sum(w.get("prompt_lines", 0) for w in group if w.get("source_fetched")) / max(sum(1 for w in group if w.get("source_fetched")), 1),
            "healthy_pct": sum(1 for w in group if w.get("health") == "healthy") / len(group),
        }

    rows = [
        ("Workflow count", "count", "d"),
        ("Avg success rate", "avg_success", "%"),
        ("Pre-step adoption", "has_pre_steps", "%"),
        ("Avg prompt lines", "avg_prompt_lines", "f"),
        ("Healthy rate", "healthy_pct", "%"),
    ]
    for label, key, fmt in rows:
        c = metrics.get("Community", {}).get(key, 0)
        g = metrics.get("GitHub/MS", {}).get(key, 0)
        if fmt == "%":
            lines.append(f"| {label} | {c:.0%} | {g:.0%} |")
        elif fmt == "d":
            lines.append(f"| {label} | {c} | {g} |")
        else:
            lines.append(f"| {label} | {c:.1f} | {g:.1f} |")

    # Top community repos by success rate
    lines.append("\n### Top 15 Community Repos (by success rate, ≥3 runs)\n")
    lines.append("| Repo | Stars | Workflows | Avg Success | Notable |")
    lines.append("|------|-------|-----------|-------------|---------|")

    repo_stats = defaultdict(lambda: {"rates": [], "stars": 0, "wf_count": 0, "features": set()})
    for w in community:
        if w["success_rate"] is not None and w["run_count"] >= 3:
            r = repo_stats[w["repo"]]
            r["rates"].append(w["success_rate"])
            r["stars"] = w["stars"]
            r["wf_count"] += 1
            if w.get("has_pre_steps"):
                r["features"].add("pre-steps")
            if w.get("has_format_spec"):
                r["features"].add("format-spec")
            if w.get("has_numbered_steps"):
                r["features"].add("structured")

    sorted_repos = sorted(
        repo_stats.items(),
        key=lambda x: (sum(x[1]["rates"]) / len(x[1]["rates"]), x[1]["stars"]),
        reverse=True,
    )
    for repo, stats in sorted_repos[:15]:
        avg_sr = sum(stats["rates"]) / len(stats["rates"])
        feats = ", ".join(stats["features"]) if stats["features"] else "—"
        lines.append(f"| [{repo}](https://github.com/{repo}) | {stats['stars']} | {stats['wf_count']} | {avg_sr:.0%} | {feats} |")

    # Trigger patterns unique to community
    lines.append("\n### Trigger Patterns: Community vs GitHub/MS\n")
    community_triggers = Counter()
    ghms_triggers = Counter()
    for w in community:
        for t in w.get("triggers", []):
            community_triggers[t] += 1
    for w in ghms:
        for t in w.get("triggers", []):
            ghms_triggers[t] += 1

    lines.append("| Trigger | Community % | GitHub/MS % | Community-heavy? |")
    lines.append("|---------|------------|------------|-----------------|")
    all_triggers = set(list(community_triggers.keys()) + list(ghms_triggers.keys()))
    for t in sorted(all_triggers):
        c_pct = community_triggers[t] / len(community) if community else 0
        g_pct = ghms_triggers[t] / len(ghms) if ghms else 0
        flag = "✅" if c_pct > g_pct * 1.5 else ""
        lines.append(f"| {t} | {c_pct:.0%} | {g_pct:.0%} | {flag} |")

    # Engine diversity
    lines.append("\n### Engine/Model Diversity\n")
    community_engines = Counter(w.get("engine", "unknown") for w in community)
    lines.append("| Engine | Count | % of Community |")
    lines.append("|--------|-------|----------------|")
    for eng, cnt in community_engines.most_common():
        lines.append(f"| {eng} | {cnt} | {cnt/len(community):.0%} |")

    # Novel patterns (features common in community but not in our pattern cards)
    lines.append("\n### Potential Novel Patterns\n")
    lines.append("Patterns observed in high-performing community workflows that may not be in the pattern library:\n")

    top_community = [w for w in community if w.get("health") == "healthy" and w.get("source_fetched")]
    if top_community:
        # Check for patterns we might not have documented
        slash_users = [w for w in top_community if "slash_command" in w.get("triggers", [])]
        discussion_users = [w for w in top_community if "discussion" in w.get("triggers", [])]
        multi_trigger = [w for w in top_community if w.get("trigger_count", 0) >= 4]
        long_prompts = [w for w in top_community if w.get("prompt_lines", 0) > 150]

        if slash_users:
            lines.append(f"- **Slash command workflows:** {len(slash_users)} healthy community workflows use slash commands")
        if discussion_users:
            lines.append(f"- **Discussion handlers:** {len(discussion_users)} healthy community workflows triggered by discussions")
        if multi_trigger:
            lines.append(f"- **Multi-trigger workflows:** {len(multi_trigger)} healthy workflows with 4+ triggers")
        if long_prompts:
            lines.append(f"- **Long-form prompts:** {len(long_prompts)} healthy workflows with 150+ line prompts")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyze agentic workflow patterns")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip source fetching (use cache)")
    parser.add_argument("--enrich-only", action="store_true", help="Only enrich, skip analysis")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze (needs enriched-registry.json)")
    parser.add_argument("--data-dir", default="data", help="Data directory")
    parser.add_argument("--output-dir", default="analysis", help="Analysis output directory")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    cache_dir = data_dir / "sources"
    cache_dir.mkdir(exist_ok=True)

    enriched_path = data_dir / "enriched-registry.json"

    if args.analyze_only:
        if not enriched_path.exists():
            print("❌ enriched-registry.json not found. Run without --analyze-only first.")
            sys.exit(1)
        workflows = json.loads(enriched_path.read_text())
    else:
        # Load scan results
        scan_path = data_dir / "scan-results.json"
        if not scan_path.exists():
            print(f"❌ {scan_path} not found.")
            sys.exit(1)

        print(f"📂 Loading {scan_path}...")
        scan_data = json.loads(scan_path.read_text())
        print(f"   {scan_data['metadata']['total_repos']} repos, {scan_data['metadata']['total_workflows']} workflows")

        # Enrich
        print(f"\n🔄 Enriching dataset (fetching sources to {cache_dir})...")
        workflows = enrich(scan_data, str(cache_dir), skip_fetch=args.skip_fetch)

        # Save enriched
        enriched_path.write_text(json.dumps(workflows, indent=2, default=str))
        print(f"💾 Saved {enriched_path} ({len(workflows)} records)")

        if args.enrich_only:
            print("✅ Enrichment complete (--enrich-only)")
            return

    # Run analyses
    print(f"\n📊 Running analyses...")

    analyses = [
        ("success-predictors", "Success Predictors", analyze_success_predictors),
        ("temporal-analysis", "Temporal Analysis", analyze_temporal),
        ("workflow-clusters", "Workflow Clustering", analyze_clustering),
        ("failure-taxonomy", "Failure Taxonomy", analyze_failures),
        ("community-patterns", "Community Patterns", analyze_community),
    ]

    for filename, title, func in analyses:
        print(f"  → {title}...")
        result = func(workflows)
        out_path = output_dir / f"{filename}.md"
        out_path.write_text(result)
        print(f"    ✅ {out_path}")

    # Summary
    print(f"\n🎉 Analysis complete!")
    print(f"   Enriched data: {enriched_path}")
    print(f"   Reports: {output_dir}/")
    for f in sorted(output_dir.glob("*.md")):
        print(f"     - {f.name}")


if __name__ == "__main__":
    main()
