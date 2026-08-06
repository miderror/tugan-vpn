from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2026-08-06T05:16:25:054228"
VERSION = "1.35.0"
DESCRIPTION = "fix_payment_pk_sql_execution"


class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="db", description=DESCRIPTION)

    async def run():
        await RawTable.raw(
            "ALTER TABLE core_payment DROP CONSTRAINT IF EXISTS core_payment_pkey CASCADE;"
        )
        await RawTable.raw(
            "ALTER TABLE core_payment ADD COLUMN IF NOT EXISTS id SERIAL PRIMARY KEY;"
        )
        await RawTable.raw(
            "ALTER TABLE core_payment DROP CONSTRAINT IF EXISTS core_payment_payment_id_key;"
        )
        await RawTable.raw(
            "ALTER TABLE core_payment ADD CONSTRAINT core_payment_payment_id_key UNIQUE (payment_id);"
        )

    manager.add_raw(run)
    return manager
