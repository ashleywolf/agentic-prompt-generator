#!/usr/bin/env python3
"""
analyze.py — Statistical analysis of agentic workflow scan data.

Reads data/scan-results.json, fetches failed run logs, computes statistics,
and outputs data/analysis-report.json for the deep-research agent.

Usage:
    python3 scripts/analyze.py                    # Full analysis with log fetching
    python3 scripts/analyze.py --skip-logs        # Stats only, no API calls
    python3 scripts/analyze.py --max-log-repos 50 # Limit log fetching to 50 repos
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DATA = REPO_ROOT / "data" / "scan-results.json"
PATTERNS_FILE = REPO_ROOT / "patterns.json"
REPORT_FILE = REPO_ROOT / "data" / "analysis-report.json"

SKIP_LOGS = "--skip-logs" in sys.argv
MAX_LOG_REPOS = 999
for i, arg in enumerate(sys.argv):
    if arg == "--max-log-repos" and i + 1 < len(sys.argv):
        MAX_LOG_REPOS = int(sys.argv[i + 1])


# ── Helpers ─────────────────────────────────────────────────────────

def parse_success_rate(sr_str):
    """Parse '8/10' → 0.8, '0/0' → None."""
    if not sr_str or sr_str == "0/0":
        return None
    try:
        num, den = sr_str.split("/")
        return int(num) / int(den) if int(den) > 0 else None
    except Exception:
        return None


def classify_workflow(wf):
    """Classify a workflow into an archetype by name heuristics."""
    name = (wf.get("name", "") + " " + wf.get("file", "")).lower()
    if "triage" in name or "label" in name:
        return "issue-triage"
    if "fix" in name or "doctor" in name or "ci" in name or "code" in name:
        return "code-improvement"
    if "report" in name or "summary" in name or "weekly" in name or "status" in name:
        return "status-report"
    if "depend" in name or "update" in name or "renovate" in name:
        return "dependency-monitor"
    if "moderat" in name or "review" in name or "content" in name:
        return "content-moderation"
    return "custom"


def fetch_failed_logs(repo, run_id):
    """Fetch job logs for a failed run, return log text or None."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/actions/runs/{run_id}/jobs",
             "-q", "[.jobs[] | select(.conclusion == \"failure\") | .id] | first"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        job_id = result.stdout.strip()

        result = subprocess.run(
            ["gh", "api", f"repos/{repo}/actions/jobs/{job_id}/logs",
             "--header", "Accept: application/vnd.github.v3+json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            # Return last 2000 chars to keep manageable
            return result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
    except Exception:
        pass
    return None


def categorize_log(log_text):
    """Categorize a log into failure types."""
    if not log_text:
        return "unknown"
    text = log_text.lower()
    if "timeout" in text or "timed out" in text or "deadline exceeded" in text:
        return "timeout"
    if "rate limit" in text or "rate_limit" in text or "429" in text or "secondary rate" in text:
        return "rate_limit"
    if "safe" in text and ("output" in text or "denied" in text or "not allowed" in text):
        return "safe_output_denied"
    if "401" in text or "403" in text or "unauthorized" in text or "permission" in text:
        return "auth_error"
    if "not found" in text or "404" in text:
        return "not_found"
    if "error" in text or "exception" in text or "traceback" in text or "failed" in text:
        return "crash"
    return "unknown"


# ── Main Analysis ───────────────────────────────────────────────────

def main():
    print("═" * 60)
    print("  Deep Research: Statistical Analysis")
    print("═" * 60)

    # Load scan data
    if not SCAN_DATA.exists():
        print(f"ERROR: {SCAN_DATA} not found. Run scan.sh first.")
        sys.exit(1)

    with open(SCAN_DATA) as f:
        scan = json.load(f)

    repos = scan.get("repos", {})
    metadata = scan.get("metadata", {})
    print(f"\n  Dataset: {metadata.get('total_repos', len(repos))} repos, "
          f"{metadata.get('total_workflows', '?')} workflows")

    # Flatten all workflows
    all_workflows = []
    for repo_key, repo in repos.items():
        for wf in repo.get("workflows", []):
            wf["_repo"] = repo_key
            wf["_stars"] = repo.get("stars", 0)
            wf["_status"] = repo.get("status", "unknown")
            all_workflows.append(wf)

    print(f"  Flattened: {len(all_workflows)} workflow entries")

    # ── 1. Trigger combo analysis ──────────────────────────────────
    print("\n  [1/8] Trigger combo analysis...")
    combo_stats = defaultdict(lambda: {"successes": 0, "total": 0, "repos": set()})

    for wf in all_workflows:
        triggers = sorted(set(wf.get("triggers", [])))
        if not triggers:
            continue
        combo_key = "+".join(triggers)
        sr = parse_success_rate(wf.get("success_rate"))

        # Count from detailed runs if available
        runs = wf.get("recent_runs_detail", [])
        if runs:
            for run in runs:
                combo_stats[combo_key]["total"] += 1
                if run.get("conclusion") == "success":
                    combo_stats[combo_key]["successes"] += 1
                combo_stats[combo_key]["repos"].add(wf["_repo"])
        elif sr is not None:
            parts = wf.get("success_rate", "0/0").split("/")
            if len(parts) == 2:
                combo_stats[combo_key]["successes"] += int(parts[0])
                combo_stats[combo_key]["total"] += int(parts[1])
                combo_stats[combo_key]["repos"].add(wf["_repo"])

    trigger_combos = []
    for combo, stats in sorted(combo_stats.items(), key=lambda x: -x[1]["total"]):
        rate = stats["successes"] / stats["total"] if stats["total"] > 0 else 0
        trigger_combos.append({
            "combo": combo,
            "success_rate": round(rate, 3),
            "successes": stats["successes"],
            "total_runs": stats["total"],
            "n_workflows": len(stats["repos"]),
            "risk": "high" if rate < 0.3 else ("medium" if rate < 0.6 else "low")
        })
    trigger_combos.sort(key=lambda x: -x["total_runs"])
    print(f"    Found {len(trigger_combos)} unique trigger combinations")

    # ── 2. Archetype health ────────────────────────────────────────
    print("  [2/8] Archetype health...")
    arch_stats = defaultdict(lambda: {"successes": 0, "total": 0, "workflows": 0, "repos": set()})

    for wf in all_workflows:
        arch = classify_workflow(wf)
        arch_stats[arch]["workflows"] += 1
        arch_stats[arch]["repos"].add(wf["_repo"])

        runs = wf.get("recent_runs_detail", [])
        if runs:
            for run in runs:
                arch_stats[arch]["total"] += 1
                if run.get("conclusion") == "success":
                    arch_stats[arch]["successes"] += 1
        else:
            sr = parse_success_rate(wf.get("success_rate"))
            if sr is not None:
                parts = wf.get("success_rate", "0/0").split("/")
                if len(parts) == 2:
                    arch_stats[arch]["successes"] += int(parts[0])
                    arch_stats[arch]["total"] += int(parts[1])

    # Load current patterns.json for comparison
    current_patterns = {}
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            pdata = json.load(f)
            for a in pdata.get("archetypes", []):
                current_patterns[a["id"]] = a.get("success_rate", 0)

    archetype_health = []
    for arch_id, stats in sorted(arch_stats.items()):
        computed = round(stats["successes"] / stats["total"], 3) if stats["total"] > 0 else 0
        current = current_patterns.get(arch_id, 0)
        delta = round(computed - current, 3)
        archetype_health.append({
            "id": arch_id,
            "current_rate": current,
            "computed_rate": computed,
            "delta": delta,
            "n_runs": stats["total"],
            "n_workflows": stats["workflows"],
            "n_repos": len(stats["repos"]),
            "significant_change": abs(delta) >= 0.05
        })
    print(f"    {len(archetype_health)} archetypes analyzed")

    # ── 3. Engine analysis ─────────────────────────────────────────
    print("  [3/8] Engine analysis...")
    engine_stats = defaultdict(lambda: {"successes": 0, "total": 0, "workflows": 0})

    for wf in all_workflows:
        engine = wf.get("engine", "default")
        engine_stats[engine]["workflows"] += 1
        runs = wf.get("recent_runs_detail", [])
        for run in runs:
            engine_stats[engine]["total"] += 1
            if run.get("conclusion") == "success":
                engine_stats[engine]["successes"] += 1

    engine_analysis = []
    for engine, stats in sorted(engine_stats.items(), key=lambda x: -x[1]["total"]):
        rate = stats["successes"] / stats["total"] if stats["total"] > 0 else 0
        engine_analysis.append({
            "engine": engine,
            "success_rate": round(rate, 3),
            "total_runs": stats["total"],
            "n_workflows": stats["workflows"]
        })
    print(f"    {len(engine_analysis)} engines found")

    # ── 4. Prompt feature correlation ──────────────────────────────
    print("  [4/8] Prompt feature correlation...")
    feature_stats = defaultdict(lambda: {"with": {"s": 0, "t": 0}, "without": {"s": 0, "t": 0}})

    for wf in all_workflows:
        runs = wf.get("recent_runs_detail", [])
        if not runs:
            continue
        successes = sum(1 for r in runs if r.get("conclusion") == "success")
        total = len(runs)

        features = {
            "has_pre_steps": wf.get("has_pre_steps", False),
            "has_workflow_dispatch": "workflow_dispatch" in (wf.get("triggers") or []),
            "has_schedule": "schedule" in (wf.get("triggers") or []),
            "has_tools": bool(wf.get("tools")),
            "has_safe_outputs": bool(wf.get("safe_outputs")),
            "source_available": wf.get("source_available", False),
        }

        for feat, present in features.items():
            bucket = "with" if present else "without"
            feature_stats[feat][bucket]["s"] += successes
            feature_stats[feat][bucket]["t"] += total

    feature_correlation = []
    for feat, stats in feature_stats.items():
        with_rate = stats["with"]["s"] / stats["with"]["t"] if stats["with"]["t"] > 0 else 0
        without_rate = stats["without"]["s"] / stats["without"]["t"] if stats["without"]["t"] > 0 else 0
        delta = round(with_rate - without_rate, 3)
        feature_correlation.append({
            "feature": feat,
            "with_rate": round(with_rate, 3),
            "with_n": stats["with"]["t"],
            "without_rate": round(without_rate, 3),
            "without_n": stats["without"]["t"],
            "delta": delta,
            "significant": abs(delta) >= 0.10 and min(stats["with"]["t"], stats["without"]["t"]) >= 10
        })
    feature_correlation.sort(key=lambda x: -abs(x["delta"]))
    print(f"    {len(feature_correlation)} features analyzed")

    # ── 5. Degradation detection ───────────────────────────────────
    print("  [5/8] Degradation detection...")
    degraded = []
    for wf in all_workflows:
        runs = wf.get("recent_runs_detail", [])
        if len(runs) < 4:
            continue
        # Split into first half and second half
        mid = len(runs) // 2
        recent = runs[:mid]
        older = runs[mid:]
        recent_rate = sum(1 for r in recent if r.get("conclusion") == "success") / len(recent)
        older_rate = sum(1 for r in older if r.get("conclusion") == "success") / len(older)
        if older_rate >= 0.7 and recent_rate <= 0.3:
            degraded.append({
                "repo": wf["_repo"],
                "workflow": wf.get("name", "unknown"),
                "older_rate": round(older_rate, 2),
                "recent_rate": round(recent_rate, 2),
                "runs_analyzed": len(runs)
            })
    degraded.sort(key=lambda x: x["recent_rate"])
    print(f"    {len(degraded)} degraded workflows found")

    # ── 6. New pattern discovery ───────────────────────────────────
    print("  [6/8] New pattern discovery...")
    name_counter = Counter()
    name_success = defaultdict(lambda: {"s": 0, "t": 0, "repos": set()})

    for wf in all_workflows:
        name = wf.get("name", "").lower().strip()
        if not name or len(name) < 3:
            continue
        # Normalize common suffixes
        name = re.sub(r'[-_](agent|bot|workflow|auto)$', '', name)
        name_counter[name] += 1
        runs = wf.get("recent_runs_detail", [])
        for run in runs:
            name_success[name]["t"] += 1
            if run.get("conclusion") == "success":
                name_success[name]["s"] += 1
        name_success[name]["repos"].add(wf["_repo"])

    # Patterns seen in 3+ repos with data
    new_patterns = []
    existing_archetypes = {"issue-triage", "code-improvement", "status-report",
                           "dependency-monitor", "content-moderation", "custom"}
    for name, count in name_counter.most_common(50):
        stats = name_success[name]
        if len(stats["repos"]) >= 3 and stats["t"] >= 5:
            rate = stats["s"] / stats["t"] if stats["t"] > 0 else 0
            arch = classify_workflow({"name": name, "file": ""})
            new_patterns.append({
                "name": name,
                "current_archetype": arch,
                "repos_seen": len(stats["repos"]),
                "total_runs": stats["t"],
                "success_rate": round(rate, 3),
            })
    new_patterns.sort(key=lambda x: -x["repos_seen"])
    print(f"    {len(new_patterns)} named patterns found across 3+ repos")

    # ── 7. Failure log analysis ────────────────────────────────────
    failure_categories = Counter()
    failure_by_archetype = defaultdict(Counter)
    log_samples = defaultdict(list)

    if not SKIP_LOGS:
        print("  [7/8] Failure log analysis (fetching logs)...")
        failed_runs = []
        for wf in all_workflows:
            for run in wf.get("recent_runs_detail", []):
                if run.get("conclusion") == "failure":
                    failed_runs.append({
                        "repo": wf["_repo"],
                        "run_id": run["id"],
                        "workflow": wf.get("name", "unknown"),
                        "archetype": classify_workflow(wf)
                    })

        # Deduplicate by repo to limit API calls
        repos_processed = set()
        logs_fetched = 0
        total_failed = len(failed_runs)
        print(f"    {total_failed} failed runs to analyze...")

        for i, fr in enumerate(failed_runs):
            if len(repos_processed) >= MAX_LOG_REPOS:
                break
            repos_processed.add(fr["repo"])

            if (i + 1) % 10 == 0:
                sys.stdout.write(f"\r    Fetching logs {i+1}/{min(total_failed, MAX_LOG_REPOS*3)}...")
                sys.stdout.flush()

            log_text = fetch_failed_logs(fr["repo"], fr["run_id"])
            category = categorize_log(log_text)
            failure_categories[category] += 1
            failure_by_archetype[fr["archetype"]][category] += 1

            # Keep a few samples per category
            if log_text and len(log_samples[category]) < 3:
                log_samples[category].append({
                    "repo": fr["repo"],
                    "workflow": fr["workflow"],
                    "snippet": log_text[-500:]
                })
            logs_fetched += 1

            import time
            time.sleep(0.3)

        sys.stdout.write("\n")
        print(f"    Fetched {logs_fetched} logs from {len(repos_processed)} repos")
    else:
        print("  [7/8] Failure log analysis (skipped — --skip-logs)")
        # Estimate from run data
        for wf in all_workflows:
            arch = classify_workflow(wf)
            for run in wf.get("recent_runs_detail", []):
                if run.get("conclusion") == "failure":
                    failure_categories["unknown"] += 1
                    failure_by_archetype[arch]["unknown"] += 1

    total_failures = sum(failure_categories.values())
    failure_analysis = {
        "total_failures": total_failures,
        "categories": {
            cat: {
                "count": count,
                "pct": round(count / total_failures, 3) if total_failures > 0 else 0,
            }
            for cat, count in failure_categories.most_common()
        },
        "by_archetype": {
            arch: dict(cats.most_common())
            for arch, cats in failure_by_archetype.items()
        },
        "log_samples": {
            cat: samples for cat, samples in log_samples.items()
        } if not SKIP_LOGS else {}
    }
    print(f"    Failure categories: {dict(failure_categories.most_common())}")

    # ── 8. Recommendations ─────────────────────────────────────────
    print("  [8/8] Generating recommendations...")
    recommendations = []

    # Trigger-based recommendations
    for tc in trigger_combos:
        if tc["total_runs"] >= 10 and tc["success_rate"] < 0.2:
            recommendations.append({
                "type": "warn_trigger",
                "message": f"Trigger combo '{tc['combo']}' has {tc['success_rate']*100:.0f}% success rate across {tc['total_runs']} runs — consider adding to anti-patterns",
                "data": tc
            })

    # Archetype drift recommendations
    for ah in archetype_health:
        if ah["significant_change"]:
            direction = "improved" if ah["delta"] > 0 else "degraded"
            recommendations.append({
                "type": "archetype_drift",
                "message": f"Archetype '{ah['id']}' has {direction}: {ah['current_rate']*100:.0f}% → {ah['computed_rate']*100:.0f}% (Δ{ah['delta']*100:+.1f}pp, n={ah['n_runs']})",
                "data": ah
            })

    # Feature recommendations
    for fc in feature_correlation:
        if fc["significant"]:
            word = "improves" if fc["delta"] > 0 else "hurts"
            recommendations.append({
                "type": "feature_correlation",
                "message": f"Feature '{fc['feature']}' {word} success rate by {abs(fc['delta'])*100:.1f}pp ({fc['with_rate']*100:.0f}% vs {fc['without_rate']*100:.0f}%)",
                "data": fc
            })

    # Degradation alerts
    for d in degraded:
        recommendations.append({
            "type": "degradation",
            "message": f"Workflow '{d['workflow']}' in {d['repo']} degraded from {d['older_rate']*100:.0f}% to {d['recent_rate']*100:.0f}%",
            "data": d
        })

    print(f"    {len(recommendations)} recommendations generated")

    # ── Build report ───────────────────────────────────────────────
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "repos": len(repos),
            "workflows": len(all_workflows),
            "with_runs": sum(1 for w in all_workflows if w.get("recent_runs_detail")),
            "total_runs_analyzed": sum(len(w.get("recent_runs_detail", [])) for w in all_workflows),
        },
        "trigger_analysis": {
            "combos": trigger_combos[:30]
        },
        "archetype_health": archetype_health,
        "engine_analysis": engine_analysis,
        "feature_correlation": feature_correlation,
        "failure_analysis": failure_analysis,
        "degraded_workflows": degraded[:20],
        "new_patterns": new_patterns[:20],
        "recommendations": recommendations,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(f"\n  ✅ Analysis report written to {REPORT_FILE}")
    print(f"     {len(trigger_combos)} trigger combos, {len(archetype_health)} archetypes, "
          f"{len(recommendations)} recommendations")
    print("═" * 60)


if __name__ == "__main__":
    main()
