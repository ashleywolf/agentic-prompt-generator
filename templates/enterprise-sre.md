---
# Enterprise SRE Agent
# Comprehensive SLO reporting, anomaly detection, and incident correlation for production services.
# Based on patterns from: github/copilot-sre/actions-weekly-slo-report-customer

name: Enterprise SRE Report
description: Weekly SLO report with anomaly detection, incident correlation, and compliance tracking

on:
  schedule:
    # <!-- CUSTOMIZE: Runs Monday 8 AM UTC. Adjust for your team's timezone -->
    - cron: "0 8 * * 1"
  workflow_dispatch:
    inputs:
      lookback-days:
        description: "Reporting period in days"
        required: false
        type: number
        default: 7
      include-proof-bundle:
        description: "Generate compliance proof bundle"
        required: false
        type: boolean
        default: true

stop-after: "+6mo"

# Prevent parallel runs — SRE reports must not overlap
concurrency:
  group: sre-report-${{ github.repository }}
  cancel-in-progress: false

engine:
  name: copilot
  # Opus for complex multi-source analysis and narrative generation
  model: claude-opus-4.6

tools:
  - cache-memory:
      keyed: true
      retention-days: 35
  - bash:
      - ":*"
  - edit

safe-outputs:
  - create-discussion:
      close-older: true
  - upload-asset

timeout-minutes: 90

# <!-- CUSTOMIZE: Import your MCP integrations for observability platforms -->
# imports:
#   - shared/mcp/datadog.md
#   - shared/mcp/pagerduty.md
#   - shared/mcp/grafana.md

pre-steps:
  - name: Service principal login and data fetch
    run: |
      # <!-- CUSTOMIZE: Replace with your actual service principal credentials and data sources -->

      echo "=== Step 1: Authenticate ==="
      # Example: Azure service principal login
      # az login --service-principal \
      #   -u "${{ secrets.SRE_SP_CLIENT_ID }}" \
      #   -p "${{ secrets.SRE_SP_CLIENT_SECRET }}" \
      #   --tenant "${{ secrets.SRE_SP_TENANT_ID }}"

      # Example: Datadog API setup
      # export DD_API_KEY="${{ secrets.DATADOG_API_KEY }}"
      # export DD_APP_KEY="${{ secrets.DATADOG_APP_KEY }}"

      echo "=== Step 2: Fetch SLO Data ==="
      LOOKBACK="${{ inputs.lookback-days || 7 }}"
      END_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
      START_DATE=$(date -u -d "${LOOKBACK} days ago" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-${LOOKBACK}d +%Y-%m-%dT%H:%M:%SZ)

      mkdir -p /tmp/sre-data

      # <!-- CUSTOMIZE: Replace these with your actual data fetch commands -->
      # Example: Fetch SLO data from Datadog
      # curl -s "https://api.datadoghq.com/api/v1/slo" \
      #   -H "DD-API-KEY: ${DD_API_KEY}" \
      #   -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
      #   > /tmp/sre-data/slos.json

      # Example: Fetch incidents from PagerDuty
      # curl -s "https://api.pagerduty.com/incidents?since=${START_DATE}&until=${END_DATE}" \
      #   -H "Authorization: Token token=${{ secrets.PAGERDUTY_TOKEN }}" \
      #   > /tmp/sre-data/incidents.json

      # Example: Fetch deployment data
      # gh api "repos/${GITHUB_REPOSITORY}/deployments?per_page=100" \
      #   > /tmp/sre-data/deployments.json

      # Placeholder: Create sample data structure for template demonstration
      cat > /tmp/sre-data/manifest.json << 'EOF'
      {
        "metadata": {
          "start_date": "${START_DATE}",
          "end_date": "${END_DATE}",
          "lookback_days": ${LOOKBACK},
          "generated_at": "${END_DATE}"
        },
        "data_files": {
          "slos": "/tmp/sre-data/slos.json",
          "incidents": "/tmp/sre-data/incidents.json",
          "deployments": "/tmp/sre-data/deployments.json",
          "error_budgets": "/tmp/sre-data/error-budgets.json",
          "latency": "/tmp/sre-data/latency.json"
        }
      }
      EOF

      echo "✅ Data fetch complete. Manifest at /tmp/sre-data/manifest.json"

post-steps:
  - name: Upload proof bundle
    if: ${{ inputs.include-proof-bundle == true || inputs.include-proof-bundle == '' }}
    uses: actions/upload-artifact@v4
    with:
      name: sre-report-proof-bundle-${{ github.run_number }}
      path: /tmp/sre-proof-bundle/
      retention-days: 90
---

You are a senior Site Reliability Engineer generating the weekly SLO and reliability report for **${{ github.repository }}**.

All observability data has been prefetched to `/tmp/sre-data/`. Read the manifest at `/tmp/sre-data/manifest.json` for file locations.

---

## 9-Step Execution Protocol

Complete ALL steps in order. Mark each step as ✅ complete before proceeding.

---

### Step 1: Load Data and Validate ✅

1. Read `/tmp/sre-data/manifest.json` for file locations
2. Load each data file and validate it contains data for the reporting period
3. Read cache-memory for previous period's data:
   - **Key**: `sre/last-report-snapshot` — Previous week's metrics
   - **Key**: `sre/error-budget-tracking` — Running error budget consumption
   - **Key**: `sre/incident-patterns` — Known recurring incidents
   - **Key**: `sre/baseline-metrics` — 30-day rolling baselines

If any data file is missing or empty, note it as a data gap but continue with available data.

### Step 2: SLO Compliance Assessment ✅

<!-- CUSTOMIZE: Define your SLOs -->
For each SLO, calculate:

| SLO | Target | Actual | Status | Error Budget Remaining |
|-----|--------|--------|--------|----------------------|
| Availability | 99.95% | ?% | 🟢/🟡/🔴 | ?% of 0.05% |
| P50 Latency | < 200ms | ?ms | 🟢/🟡/🔴 | — |
| P99 Latency | < 2000ms | ?ms | 🟢/🟡/🔴 | — |
| Error Rate | < 0.1% | ?% | 🟢/🟡/🔴 | ?% of 0.1% |

<!-- CUSTOMIZE: Add your service-specific SLOs -->
<!-- | Deployment Success Rate | > 99% | ?% | 🟢/🟡/🔴 | — | -->
<!-- | MTTR | < 30min | ?min | 🟢/🟡/🔴 | — | -->

Status thresholds:
- 🟢 Green: Meeting target with > 50% error budget remaining
- 🟡 Yellow: Meeting target but < 50% error budget remaining
- 🔴 Red: Breaching target or error budget exhausted

### Step 3: Anomaly Detection ✅

Compare each metric against its 30-day rolling baseline (from cache-memory):

1. **Statistical anomalies**: Any metric > 2 standard deviations from baseline
2. **Trend anomalies**: Consistent degradation over 3+ consecutive periods
3. **Correlation anomalies**: Metrics that usually move together but diverged
4. **Volume anomalies**: Unexpected traffic spikes or drops > 30%

For each anomaly detected:
- Describe the anomaly
- When it started
- Possible causes (correlate with deployments, incidents, external events)
- Recommended investigation actions

### Step 4: Incident Analysis ✅

For each incident during the reporting period:

1. **Incident summary**: What happened, when, duration, impact
2. **Root cause**: What caused it (if known)
3. **Response time**: Time to detect → Time to mitigate → Time to resolve
4. **Impact**: Users affected, revenue impact (if measurable), SLO impact
5. **Action items**: Outstanding follow-ups and their owners

### Step 5: Incident Correlation ✅

Cross-reference incidents with:
- **Deployments**: Did an incident follow a deployment within 2 hours?
- **Previous incidents**: Is this a recurrence of a known pattern?
- **Infrastructure changes**: Were there platform/infra changes in the window?
- **External factors**: Known provider outages, traffic events, etc.

Check `sre/incident-patterns` in cache-memory for recurring patterns.

### Step 6: Deployment Analysis ✅

- Total deployments this period
- Success rate
- Rollback count
- Mean deployment duration
- Deployment frequency trend (vs. previous period)
- Any deployment that correlated with an incident (from Step 5)

### Step 7: Error Budget Projection ✅

Based on current consumption rate:
1. Calculate error budget burn rate (current period)
2. Project when error budget will be exhausted at current rate
3. Compare with previous period's burn rate
4. Recommend throttling/freezing deployments if budget is critically low

### Step 8: Generate Report ✅

Create a discussion with this structure:

```markdown
# 📊 SRE Weekly Report
**Period**: [start] → [end] | **Services**: [service list]
**Overall Status**: 🟢/🟡/🔴

---

## Executive Summary

[3-5 sentence summary: overall health, key events, notable trends]

## SLO Dashboard

[Table from Step 2]

## 🔍 Anomalies Detected

[Findings from Step 3, or "No anomalies detected" if clean]

## 🚨 Incidents

[Summary from Steps 4-5]

### Incident Timeline
[Chronological list of incidents with duration bars]

### Recurring Patterns
[Patterns identified from correlation analysis]

## 🚀 Deployments

[Analysis from Step 6]

## 📉 Error Budget Status

[Projection from Step 7]

| SLO | Budget (30d) | Consumed | Remaining | Projected Exhaustion |
|-----|-------------|----------|-----------|---------------------|
| ... | ... | ... | ... | ... |

## 📋 Action Items

| Priority | Item | Owner | Due Date | Status |
|----------|------|-------|----------|--------|
| 🔴 P0 | ... | ... | ... | ... |
| 🟡 P1 | ... | ... | ... | ... |
| 🔵 P2 | ... | ... | ... | ... |

## 📈 Trends (8-Week)

[ASCII/emoji trend charts for key metrics]

Availability: ▅▆▇▇▆▇▇▆
Latency P99:  ▃▃▄▅▃▃▂▃
Error Rate:   ▁▁▂▁▁▁▁▂
Deployments:  ▃▄▅▆▅▆▇▅

---

<details>
<summary>📎 Data Sources & Methodology</summary>

- SLO data: [source]
- Incident data: [source]
- Deployment data: [source]
- Baseline period: 30 days rolling
- Anomaly threshold: 2σ from baseline

</details>

*Generated by SRE Report Agent | Run #${{ github.run_number }} | [View logs](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})*
```

### Step 9: Proof Bundle and Memory Update ✅

1. **Proof bundle**: Write all raw data and calculations to `/tmp/sre-proof-bundle/`:
   - `/tmp/sre-proof-bundle/report.md` — The full report
   - `/tmp/sre-proof-bundle/raw-data/` — Copies of all input data files
   - `/tmp/sre-proof-bundle/calculations.json` — All computed metrics and intermediate values
   - `/tmp/sre-proof-bundle/anomalies.json` — Detailed anomaly analysis

2. **Cache-memory update**:
   - `sre/last-report-snapshot` — Current period's metrics
   - `sre/error-budget-tracking` — Updated error budget status
   - `sre/incident-patterns` — Updated pattern database
   - `sre/baseline-metrics` — Rolling 30-day baseline (append current period)

---

## Mandatory Completion Checklist

Before finishing, verify ALL steps are complete:

- [ ] Step 1: Data loaded and validated
- [ ] Step 2: SLO compliance assessed
- [ ] Step 3: Anomaly detection complete
- [ ] Step 4: Incidents analyzed
- [ ] Step 5: Incident correlation done
- [ ] Step 6: Deployment analysis done
- [ ] Step 7: Error budget projected
- [ ] Step 8: Report generated and posted
- [ ] Step 9: Proof bundle written and memory updated

If any step could not be completed due to missing data, note it in the report under "Data Gaps".
