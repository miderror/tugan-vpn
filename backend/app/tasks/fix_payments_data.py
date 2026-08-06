import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from piccolo.engine import engine_finder
from piccolo.querystring import QueryString

db_engine = engine_finder()



async def fix_payments_and_schema(json_file_path: str):
    print(f"[+] Чтение {json_file_path} и обновление payment_id...")
    with open(json_file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    updates_count = 0
    for item in raw_data:
        if item.get("model", "").endswith(".payment"):
            pk = str(item.get("pk"))
            fields = item.get("fields", {})
            real_payment_id = fields.get("payment_id")

            if real_payment_id and real_payment_id != pk:
                await db_engine.run_querystring(
                    QueryString(
                        "UPDATE core_payment SET payment_id = {} WHERE payment_id = {}",
                        real_payment_id,
                        pk,
                    )
                )
                updates_count += 1

    print(f"[SUCCESS] Обновлено {updates_count} старых платежей!")


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "data_logic.json"
    asyncio.run(fix_payments_and_schema(file_path))