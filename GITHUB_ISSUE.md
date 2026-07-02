# [SEV-2][DQ Incident] AdventureWorks ingestion blocked by Snowflake privilege regression

## Summary

The `adventureworks` Fivetran connector failed to sync into Snowflake because its service role no longer had sufficient privileges on the `AWS_STACK_1_BRONZE` database.

This caused stale source data, failed data quality checks, and downstream impact across sales, customer, finance, and executive reporting assets.

Detected incident: `PTM-198`  
Severity: `SEV-2`  
Environment: `production`  
Primary system boundary: `Fivetran → Snowflake`

---

## What happened?

The `adventureworks` ingestion job failed during sync with a Snowflake access control error.

```text
SQL access control error:
Insufficient privileges to operate on database 'AWS_STACK_1_BRONZE'
```

Because the bronze layer was not refreshed, downstream dbt models and dashboards continued to use stale source data.

---

## Why did it happen?

The Snowflake role used by the Fivetran connector, `FIVETRAN_ADVENTUREWORKS_ROLE`, was missing required privileges on the destination database and schema.

Likely root cause:

```text
A recent Snowflake role cleanup, permission refactor, or manual grant change removed privileges required by the AdventureWorks connector.
```

Contributing factors:

- Required Snowflake grants were not fully managed in version control.
- CI did not validate connector permissions before deployment.
- The data contract defined freshness expectations but did not explicitly enforce required warehouse access.
- Observability detected the failure, but the incident did not automatically map to the owning repo, grant file, and remediation path.

---

## Where did it happen?

| Field | Value |
|---|---|
| Source system | `AdventureWorks` |
| Connector | `fivetran/adventureworks` |
| Warehouse | `Snowflake` |
| Database | `AWS_STACK_1_BRONZE` |
| Schema | `ADVENTUREWORKS` |
| Role | `FIVETRAN_ADVENTUREWORKS_ROLE` |
| Layer | `Bronze` |
| Environment | `production` |

---

## What was impacted?

### Directly impacted assets

| Asset | Impact |
|---|---|
| `fivetran/adventureworks` | Connector sync failed |
| `AWS_STACK_1_BRONZE.ADVENTUREWORKS` | Bronze tables stale |
| `_fivetran_synced` freshness | SLA breached |

### Downstream models impacted

| Layer | Model | Impact |
|---|---|---|
| Staging | `stg_adventureworks__orders` | Stale order data |
| Staging | `stg_adventureworks__customers` | Stale customer data |
| Intermediate | `int_sales_order_enriched` | Incomplete or stale enrichment |
| Mart | `fct_sales` | Stale revenue metrics |
| Mart | `dim_customer` | Stale customer attributes |

### Data quality checks impacted

| Check | Expected | Actual |
|---|---|---|
| `source_freshness_adventureworks_orders` | Source data refreshed within 2 hours | Failed |
| `row_count_anomaly_fct_sales` | Row count within expected range | Failed or at risk |
| `not_null_orders_order_id` | Passing | At risk due stale upstream |
| `relationships_sales_customer` | Passing | At risk due stale upstream |

---

## Who was impacted?

Primary impacted teams:

- Finance Analytics
- Revenue Operations
- Sales Leadership
- Customer Success Operations
- Executive Reporting Consumers

Primary impacted use cases:

- Daily revenue reporting
- Sales performance monitoring
- Finance close preparation
- Customer retention reporting
- Executive KPI dashboards

---

## Associated cost or risk

### Business risk

Revenue, sales, and customer reporting may be stale or incomplete. Stakeholders could make business decisions using outdated metrics.

### Operational risk

The same permission regression pattern could affect other Fivetran connectors if Snowflake grants are not codified and validated consistently.

### Estimated impact

| Metric | Estimate |
|---|---:|
| Downstream pipelines affected | 55 |
| Production dashboards stale | 4 |
| Freshness delay | 6+ hours |
| Engineering remediation | 2–4 hours |
| Analyst validation | 2–6 hours |
| Potential reporting delay | 1 business day |

---

## Recommended next step

Open a remediation PR that:

1. Restores required Snowflake privileges for `FIVETRAN_ADVENTUREWORKS_ROLE`.
2. Moves the required grants into version-controlled infrastructure.
3. Adds a CI preflight check that fails when connector privileges are missing.
4. Updates the AdventureWorks data contract with ownership, freshness SLA, required access, and downstream lineage.
5. Adds validation steps for source freshness, dbt tests, and dashboard recovery.

---

## Remediation tasks

### Phase 1 — Restore service

- [ ] Restore required Snowflake grants for `FIVETRAN_ADVENTUREWORKS_ROLE`
- [ ] Trigger Fivetran resync for `adventureworks`
- [ ] Confirm bronze tables are updating
- [ ] Run dbt source freshness checks
- [ ] Backfill or rerun impacted downstream models

### Phase 2 — Validate data quality

- [ ] Validate row counts for `orders`, `customers`, and `sales`
- [ ] Confirm `_fivetran_synced` is within SLA
- [ ] Run dbt tests for impacted staging, intermediate, and mart models
- [ ] Confirm dashboards are no longer stale
- [ ] Notify Finance Analytics and Revenue Operations

### Phase 3 — Prevent recurrence

- [ ] Add Snowflake grants to version-controlled infrastructure
- [ ] Add connector permission preflight check in CI
- [ ] Add required access policy to the data contract
- [ ] Add lineage-aware incident metadata
- [ ] Add runbook link for Fivetran/Snowflake access failures

---

## Acceptance criteria

- [ ] `fivetran/adventureworks` sync completes successfully in production
- [ ] `AWS_STACK_1_BRONZE.ADVENTUREWORKS` tables are refreshed
- [ ] Source freshness checks pass
- [ ] Downstream dbt models complete successfully
- [ ] Impacted dashboards show current data
- [ ] Snowflake grants are defined in version control
- [ ] CI fails if required grants are removed
- [ ] Data contract includes owner, freshness SLA, access policy, and downstream lineage
- [ ] Incident is closed with validation evidence

---

## Suggested labels

`incident`, `data-quality`, `snowflake`, `fivetran`, `dbt`, `lineage`, `sev-2`, `needs-remediation`
