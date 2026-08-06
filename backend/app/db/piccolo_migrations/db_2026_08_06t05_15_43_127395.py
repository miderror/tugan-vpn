from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Varchar
from piccolo.columns.indexes import IndexMethod

ID = "2026-08-06T05:15:43:127395"
VERSION = "1.35.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="db", description=DESCRIPTION, fake=True
    )

    manager.add_column(
        table_class_name="Payment",
        tablename="core_payment",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.alter_column(
        table_class_name="Payment",
        tablename="core_payment",
        column_name="payment_id",
        db_column_name="payment_id",
        params={"primary_key": False, "unique": True, "index": True},
        old_params={"primary_key": True, "unique": False, "index": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
