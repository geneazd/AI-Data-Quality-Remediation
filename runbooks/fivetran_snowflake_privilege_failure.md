# Runbook: Fivetran Snowflake Privilege Failure

## Purpose

Use this runbook when a Fivetran connector fails to sync into Snowflake due to an access control or insufficient privileges error.

Example error:

```text
SQL access control error:
Insufficient privileges to operate on database 'AWS_STACK_1_BRONZE'
```

## Severity guidance

Treat the incident as `SEV-2` when the failed connector powers production reporting, finance metrics, executive dashboards, or customer-facing analytics.

## Immediate response

1. Confirm the failed connector and destination.
2. Capture the exact Snowflake error from the connector logs.
3. Identify the connector role.
4. Confirm the latest successful sync time.
5. Check source freshness SLA and downstream lineage.
6. Notify impacted business and technical owners.

## Diagnostic queries

Check grants assigned to the connector role:

```sql
SHOW GRANTS TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;
```

Confirm database and schema access:

```sql
USE ROLE FIVETRAN_ADVENTUREWORKS_ROLE;
USE DATABASE AWS_STACK_1_BRONZE;
USE SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS;
```

Check freshness of Fivetran-managed tables:

```sql
SELECT
  MAX(_FIVETRAN_SYNCED) AS latest_sync_at,
  DATEDIFF('minute', MAX(_FIVETRAN_SYNCED), CURRENT_TIMESTAMP()) AS freshness_lag_minutes
FROM AWS_STACK_1_BRONZE.ADVENTUREWORKS.ORDERS;
```

## Remediation

1. Restore required grants using `infra/snowflake/grants/adventureworks_fivetran.sql`.
2. Trigger a Fivetran resync.
3. Confirm new rows are landing in Snowflake.
4. Run dbt source freshness:

```bash
dbt source freshness --select source:adventureworks
```

5. Run dbt tests for impacted assets:

```bash
dbt test --select source:adventureworks+
```

6. Rebuild downstream models if required:

```bash
dbt build --select source:adventureworks+
```

## Validation checklist

- [ ] Fivetran sync completes successfully
- [ ] `_fivetran_synced` is within SLA
- [ ] dbt source freshness passes
- [ ] dbt tests pass
- [ ] Downstream models rebuilt successfully
- [ ] Impacted dashboards are current
- [ ] Business stakeholders notified

## Prevention

- Keep Snowflake grants in version control.
- Add CI validation for connector role privileges.
- Keep data contracts updated with access policies and ownership.
- Attach lineage and dashboard impact to observability alerts.
