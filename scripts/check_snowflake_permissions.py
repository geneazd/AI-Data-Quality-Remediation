#!/usr/bin/env python3
"""
scripts/check_snowflake_permissions.py

Validates that the AdventureWorks Fivetran role has the minimum Snowflake
privileges required by the data contract.

Intended usage:
  python scripts/check_snowflake_permissions.py

Required environment variables:
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_USER
  SNOWFLAKE_PASSWORD
  SNOWFLAKE_WAREHOUSE

Optional environment variables:
  SNOWFLAKE_ROLE        default: SECURITYADMIN
  FIVETRAN_ROLE_NAME    default: FIVETRAN_ADVENTUREWORKS_ROLE
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Iterable, Set, Tuple

import snowflake.connector


ROLE_NAME = os.environ.get("FIVETRAN_ROLE_NAME", "FIVETRAN_ADVENTUREWORKS_ROLE")


@dataclass(frozen=True)
class RequiredGrant:
    privilege: str
    granted_on: str
    name: str

    def as_tuple(self) -> Tuple[str, str, str]:
        return (
            self.privilege.upper(),
            self.granted_on.upper(),
            self.name.upper(),
        )


REQUIRED_GRANTS = [
    RequiredGrant("USAGE", "DATABASE", "AWS_STACK_1_BRONZE"),
    RequiredGrant("USAGE", "SCHEMA", "AWS_STACK_1_BRONZE.ADVENTUREWORKS"),
    RequiredGrant("CREATE TABLE", "SCHEMA", "AWS_STACK_1_BRONZE.ADVENTUREWORKS"),
    RequiredGrant("CREATE STAGE", "SCHEMA", "AWS_STACK_1_BRONZE.ADVENTUREWORKS"),
    RequiredGrant("CREATE FILE FORMAT", "SCHEMA", "AWS_STACK_1_BRONZE.ADVENTUREWORKS"),
]


REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
]


def validate_environment() -> None:
    missing = [key for key in REQUIRED_ENV_VARS if not os.environ.get(key)]
    if missing:
        print("Missing required environment variables:")
        for key in missing:
            print(f"- {key}")
        sys.exit(2)


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ.get("SNOWFLAKE_ROLE", "SECURITYADMIN"),
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


def normalize_grant_row(row: Iterable[object]) -> Tuple[str, str, str]:
    """
    Snowflake `SHOW GRANTS TO ROLE` typically returns columns in this order:
      created_on, privilege, granted_on, name, granted_to, grantee_name,
      grant_option, granted_by, granted_by_role_type

    We only need privilege, granted_on, and object name.
    """
    values = list(row)
    return (
        str(values[1]).upper(),
        str(values[2]).upper(),
        str(values[3]).upper(),
    )


def fetch_current_grants(cursor) -> Set[Tuple[str, str, str]]:
    cursor.execute(f"SHOW GRANTS TO ROLE {ROLE_NAME}")
    return {normalize_grant_row(row) for row in cursor.fetchall()}


def find_missing_grants(
    required_grants: Iterable[RequiredGrant],
    actual_grants: Set[Tuple[str, str, str]],
) -> list[RequiredGrant]:
    return [grant for grant in required_grants if grant.as_tuple() not in actual_grants]


def main() -> int:
    validate_environment()

    with get_connection() as conn:
        cursor = conn.cursor()
        actual_grants = fetch_current_grants(cursor)

    missing_grants = find_missing_grants(REQUIRED_GRANTS, actual_grants)

    if missing_grants:
        print(f"Missing required Snowflake grants for role: {ROLE_NAME}")
        for grant in missing_grants:
            print(f"- GRANT {grant.privilege} ON {grant.granted_on} {grant.name} TO ROLE {ROLE_NAME};")
        return 1

    print(f"All required Snowflake grants are present for role: {ROLE_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
