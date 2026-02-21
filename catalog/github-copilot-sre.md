# github/copilot-sre

> **SRE tooling for GitHub Copilot infrastructure** · [github/copilot-sre](https://github.com/github/copilot-sre)

| Field | Value |
|-------|-------|
| **Status** | 🟢 Active |
| **Workflows** | 1 |
| **Last Run** | Weekly (schedule) |
| **Primary Model** | claude-opus-4.6 |

---

## Why This Repo Is Notable

`actions-weekly-slo-report` is the **most complex single workflow analyzed** in this catalog. It combines `claude-opus-4.6` for deep reasoning, keyed cache-memory with 35-day retention for trend analysis, Datadog MCP server for metrics ingestion, an Azure service principal pre-step for authentication, proof bundle artifact uploads for audit trails, and cross-incident correlation. This is the ceiling of what a single agentic workflow can do today.

---

## Workflow Table

| # | Workflow | Trigger | Model | Archetype |
|---|----------|---------|-------|-----------|
| 1 | `actions-weekly-slo-report` | `schedule: weekly` | claude-opus-4.6 | [Reporter](../patterns/workflow-archetypes.md) |

---

## Key Patterns

### Keyed Cache-Memory (35-Day Retention)
Uses cache-memory with explicit keys and a 35-day TTL to store SLO metrics across runs. Each week's data is stored under a date-keyed entry, enabling the agent to compute week-over-week trends and flag regressions.
- **State pattern**: [Cache-memory with keys](../patterns/state-management.md)

### Datadog MCP Import
The workflow imports a Datadog MCP server configuration, giving the agent direct access to query Datadog metrics, dashboards, and monitors during execution.
- **Data pattern**: [MCP server data ingestion](../patterns/data-ingestion.md)
- **Import pattern**: [Shared Components](../patterns/shared-components.md)

### Azure Service Principal Pre-Step
A pre-step authenticates with Azure using a service principal, enabling the agent to query Azure-hosted infrastructure metrics as part of SLO reporting.
- **Data pattern**: [Pre-step authentication](../patterns/data-ingestion.md)

### Proof Bundle Artifact Upload
After generating the report, the workflow uploads a "proof bundle" as a GitHub Actions artifact — containing raw data, computed metrics, and the final report. This provides an audit trail for SLO compliance.
- **Output pattern**: [Artifact uploads](../patterns/output-selection.md)

### Incident Correlation
The agent cross-references SLO violations with recent incidents (from GitHub Issues labeled `incident`), automatically linking degradations to their root causes in the report.

### `claude-opus-4.6` (Premium Model)
Uses the most capable model available because SLO reporting requires:
- Complex multi-source data synthesis
- Trend analysis over 5-week windows
- Nuanced incident correlation
- Executive-readable narrative generation
- **Model pattern**: [Model selection — premium tier](../patterns/model-selection.md)

---

## Links to Live Files

- [`.github/agents/` directory](https://github.com/github/copilot-sre/tree/main/.github/agents)
- [`actions-weekly-slo-report.md`](https://github.com/github/copilot-sre/blob/main/.github/agents/actions-weekly-slo-report.md)
