# AdventureWorks DQ Remediation PR Files

This directory contains the files for a mock remediation PR for incident `PTM-198`.

## Included files

```text
infra/snowflake/grants/adventureworks_fivetran.sql
contracts/adventureworks/orders.yml
models/sources/adventureworks.yml
scripts/check_snowflake_permissions.py
.github/workflows/data-quality-preflight.yml
runbooks/fivetran_snowflake_privilege_failure.md
GITHUB_ISSUE.md
PULL_REQUEST_TEMPLATE.md
```

## Suggested PR title

```text
fix(adventureworks): restore Fivetran Snowflake grants and add DQ preflight safeguards
```

## Suggested validation commands

```bash
python scripts/check_snowflake_permissions.py
dbt source freshness --select source:adventureworks
dbt test --select source:adventureworks+
dbt build --select source:adventureworks+
```

## Notes

Before using this in a real environment, verify:

- The Snowflake database, schema, and role names match your environment.
- The Fivetran connector actually requires each listed privilege.
- GitHub Actions secrets exist for Snowflake connectivity.
- The dbt source names match your project conventions.
