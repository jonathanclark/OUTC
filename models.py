"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, db, today, T

db.define_table(
    "clubs",
    Field("name", length=8, unique=True),
)

db.define_table(
    "contacts",
    Field("reference", length=9, unique=True),
    Field("name", length=25),
    Field("club", "reference clubs"),
)

db.define_table(
    "coa",
    Field("code", length=6, unique=True),
    Field("description", length=33),
    Field("type", length=20),
    Field("tax_code", length=3),
)

db.define_table(
    "input_rows",
    Field(
        "member",
        "reference contacts",
        length=25,
        requires=IS_IN_DB(db, "contacts.id", "%(name)s"),
        filter_out=lambda x: x.name if x else '',
        #represent=lambda row: row.name if row else "N/A",
        #represent=lambda c: " ".join([c.name, c.reference]) if c else "N/A",
    ),
    Field(
        "account",
        "reference coa",
        requires=IS_IN_DB(db, "coa.id", "%(description)s", zero="...."),
        filter_out=lambda x: x.description if x else '',
    ),
    Field("invoice_number", length=12),
    Field(
        "invoice_date",
        "date",
        requires=IS_DATE(),
        # represent=lambda x: parse(x).strftime("%m/%d/%Y")
        # if x and isinstance(x, str)
        # else "",
        default=today,
        # required=True,
    ),
    # Field('due_date'),
    # Field('account_code', 'reference coa'),
    # Field('extra_description', length=20),
    # Field('quantity', 'integer', requires=IS_EQUAL_TO(1, 'Value must be 1')),
    # Field('amount', 'integer'),
)

db.commit()
