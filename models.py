"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, db, today, T
from datetime import timedelta
from decimal import Decimal

db.define_table(
    "clubs",
    Field("name", length=8, unique=True),
    format="%(name)s",
)

db.define_table(
    "contacts",
    Field("sageid", length=9, required=True, unique=True,),
    Field("name", length=25, required=True, unique=True,),
    Field("club", "reference clubs", required=True,),
    format="%(name)s",
)

db.define_table(
    "coa",
    Field("code", length=6, unique=True),
    Field("description", length=33),
    Field("type", length=20),
    Field("tax_code", length=6, default="No VAT"),
    format="%(description)s",
)

db.define_table(
    "input_rows",
    Field(
        "member",
        db.contacts,
    ),
    Field(
        "account",
        db.coa,
    ),
    Field("invoice_number", length=12, default=""),
    Field(
        "invoice_date",
        "date",
        requires=IS_EMPTY_OR(IS_DATE()),
        default="",
    ),
    Field(
        "due_date",
        "date",
        requires=IS_EMPTY_OR(IS_DATE()),
        default="",
    ),
    Field(
        "description_datetime",
        "datetime",
        requires=IS_EMPTY_OR(IS_DATETIME()),
    ),
    Field("description_text", length=20),
    Field("quantity", "integer", default=1),
    Field(
        "price",
        requires=IS_DECIMAL_IN_RANGE(
            -5000,
            5000,
        ),
    ),
    Field("down_loaded", "boolean", readable=False, writable=False, default=False),
)

db.commit()
