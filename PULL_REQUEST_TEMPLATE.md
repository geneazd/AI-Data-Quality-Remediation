# fix(adventureworks): restore Fivetran Snowflake grants and add DQ preflight safeguards

## Summary

This PR remediates incident `PTM-198`, where the `adventureworks` Fivetran connector failed to sync into Snowflake due to missing privileges on `AWS_STACK_1_BRONZE`.

The fix restores required Snowflake grants, codifies the access policy, adds source freshness checks, and introduces a CI preflight validation to prevent future permission regressions from reaching production.

Closes #[ISSUE_NUMBER]

---

## Root cause

The Fivetran connector role `FIVETRAN_ADVENTUREWORKS_ROLE` no longer had sufficient privileges on the Snowflake destination database and schema.

Connector error:

```text
SQL access control error:
Insufficient privileges to operate on database 'AWS_STACK_1_BRONZE'
```

---

## What changed?

| Area | Change |
|---|---|
| Snowflake grants | Restored required privileges for `FIVETRAN_ADVENTUREWORKS_ROLE` |
| Data contract | Added freshness SLA, owners, access policy, and downstream lineage |
| dbt source config | Added source freshness and quality checks |
| CI/CD | Added Snowflake permission preflight validation |
| Observability context | Added metadata for owner-aware incident routing |

---

## Files changed

```text
infra/snowflake/grants/adventureworks_fivetran.sql
contracts/adventureworks/orders.yml
models/sources/adventureworks.yml
scripts/check_snowflake_permissions.py
.github/workflows/data-quality-preflight.yml
runbooks/fivetran_snowflake_privilege_failure.md
```

---

## Test plan

- [ ] Applied Snowflake grant script in lower environment
- [ ] Ran permission preflight check successfully
- [ ] Triggered Fivetran sync for `adventureworks`
- [ ] Confirmed `_fivetran_synced` updated in bronze tables
- [ ] Ran `dbt source freshness --select source:adventureworks`
- [ ] Ran `dbt test --select source:adventureworks+`
- [ ] Rebuilt impacted downstream models
- [ ] Confirmed impacted dashboards are no longer stale

---

## Validation evidence

| Check | Result |
|---|---|
| Fivetran sync | Pending |
| Snowflake grant validation | Pending |
| dbt source freshness | Pending |
| dbt tests | Pending |
| Downstream model rebuild | Pending |
| Dashboard freshness validation | Pending |

---

## Risk

Risk level: `Low to Medium`

The grant changes are scoped to:

```text
Role: FIVETRAN_ADVENTUREWORKS_ROLE
Database: AWS_STACK_1_BRONZE
Schema: ADVENTUREWORKS
```

No broad account-level privileges are introduced.

The main risk is over-permissioning the connector role. This PR limits access to the AdventureWorks bronze schema and only grants the privileges required for ingestion.

---

## Rollback plan

If this change causes unexpected behavior:

1. Revoke newly added grants from `FIVETRAN_ADVENTUREWORKS_ROLE`.
2. Revert this PR.
3. Pause the `adventureworks` Fivetran connector if sync behavior is unsafe.
4. Restore the previous role configuration from Snowflake access history.
5. Re-run dbt freshness and downstream model checks after rollback.

---

## Reviewer checklist

- [ ] Grants are scoped only to `AWS_STACK_1_BRONZE.ADVENTUREWORKS`
- [ ] No broad account-level or warehouse-wide privileges were introduced
- [ ] Required privileges match the Fivetran connector’s actual needs
- [ ] dbt freshness SLA matches the data contract
- [ ] Contract includes owner, escalation channel, access policy, and lineage
- [ ] CI check fails closed when grants are missing
- [ ] Runbook exists for future Snowflake/Fivetran access failures

---

## Post-merge checklist

- [ ] Apply grants in production
- [ ] Trigger AdventureWorks Fivetran resync
- [ ] Confirm bronze tables are refreshed
- [ ] Rebuild impacted dbt models
- [ ] Validate dashboards
- [ ] Update incident `PTM-198`
- [ ] Notify impacted stakeholders
