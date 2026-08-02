from enum import Enum

from piccolo.columns import (
    BigInt,
    Boolean,
    Integer,
    Numeric,
    Serial,
    Text,
    Timestamptz,
    Varchar,
)
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.table import Table


class User(Table, tablename="core_user"):
    tg_id = BigInt(primary_key=True, auto_increment=False)
    username = Varchar(length=32, null=True, index=True)
    first_name = Varchar(length=64, null=True)
    last_name = Varchar(length=64, null=True)
    language_code = Varchar(length=10, null=True)

    utm_source = Varchar(length=64, null=True)

    email = Varchar(length=255, unique=True, index=True)
    sub_id = Varchar(length=255, unique=True)
    client_id = Varchar(length=255, unique=True)
    access_token = Varchar(length=255, unique=True, index=True)

    used_bytes = BigInt(default=0)
    is_active_vpn = Boolean(default=True, index=True)
    expiry_date = Timestamptz(index=True)
    next_reset_date = Timestamptz(null=True, index=True)

    claimed_gift = Boolean(default=False)
    tried_to_connect = Boolean(default=False)

    created_at = Timestamptz(default=TimestamptzNow())
    updated_at = Timestamptz(default=TimestamptzNow())


class Referral(Table, tablename="core_referral"):
    referred_id = BigInt(primary_key=True, auto_increment=False)
    referrer_id = BigInt(index=True)


class NodeTypeChoices(str, Enum):
    XUI_V2 = "3x-ui-v2"


class Node(Table, tablename="core_node"):
    id = Serial(primary_key=True)

    api_url = Varchar(length=255)
    subscription_url = Varchar(length=255)
    inbound_id = Integer(default=1)

    node_type = Varchar(
        length=32,
        default=NodeTypeChoices.XUI_V2.value,
        choices=NodeTypeChoices,
    )
    username = Varchar(length=128, null=True)
    password = Varchar(length=255, secret=True)

    is_active = Boolean(default=True, index=True)

    config_template = Text(default="")


class Tariff(Table, tablename="core_tariff"):
    id = Serial(primary_key=True)
    display_name = Varchar(length=64)
    duration_days = Integer()
    price = Numeric(digits=(10, 2))
    original_price = Numeric(digits=(10, 2), null=True)
    is_bestseller = Boolean(default=False)
    is_active = Boolean(default=True, index=True)


class Payment(Table, tablename="core_payment"):
    payment_id = Varchar(length=64, primary_key=True, auto_increment=False)
    tg_id = BigInt(index=True)
    tariff_id = Integer()
    amount = Numeric(digits=(10, 2))
    created_at = Timestamptz(default=TimestamptzNow())
