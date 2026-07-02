-- infra/snowflake/grants/adventureworks_fivetran.sql
--
-- Purpose:
-- Restore and codify the minimum Snowflake privileges required for the
-- AdventureWorks Fivetran connector to write into the bronze schema.
--
-- Incident:
-- PTM-198 - AdventureWorks ingestion failed with:
-- SQL access control error: Insufficient privileges to operate on database 'AWS_STACK_1_BRONZE'
--
-- Notes:
-- - Run as SECURITYADMIN or another role allowed to manage grants.
-- - Keep grants scoped to the AdventureWorks bronze schema.
-- - Avoid account-wide or database-wide table grants unless explicitly required.

USE ROLE SECURITYADMIN;

-- Database and schema access
GRANT USAGE ON DATABASE AWS_STACK_1_BRONZE
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

GRANT USAGE ON SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

-- Object creation required by ingestion/replication tooling
GRANT CREATE TABLE ON SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

GRANT CREATE STAGE ON SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

GRANT CREATE FILE FORMAT ON SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

-- DML on existing connector-managed tables
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
ON ALL TABLES IN SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;

-- DML on future connector-managed tables
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
ON FUTURE TABLES IN SCHEMA AWS_STACK_1_BRONZE.ADVENTUREWORKS
TO ROLE FIVETRAN_ADVENTUREWORKS_ROLE;
