import csv
import datetime
from decimal import Decimal
from io import StringIO

from py4web import URL, Field, Flash, abort, action, redirect, request, response
from py4web.utils.form import Form
from py4web.utils.grid import Column, Grid

from .menu import make_title, make_navbar, menu_structure
from py4web.utils.factories import Inject

# from py4web.utils.factories import Inject
from pydal.validators import *
from yatl.helpers import *

from .common import (
    GRID_DEFAULTS,
    T,
    auth,
    authenticated,
    cache,
    db,
    flash,
    logger,
    session,
    unauthenticated,
)
from .data_utils import input_row_to_dict


@action("delete/<record:int>", method=["GET", "POST"])
@action.uses(
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def delete(record=None):
    message = ""
    if record:
        db(db.input_rows.id == record).delete()
        db.commit()
    redirect(URL("index"))


@action("clear", method=["GET", "POST"])
@action.uses(
    session,
    db,
    flash,
)
def clear():
    # breakpoint()
    query = db.input_rows.down_loaded == False
    print(f"Number of recs before = {db(query).count()}")
    db(query).update(down_loaded=True)
    print(f"Number of recs after = {db(query).count()}")
    db.commit()
    redirect(URL("index"))


@action("edit/<record_id:int>", method=["GET", "POST"])
@action.uses(
    "edit_form.html",
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def edit(record_id):
    message = ""
    db.input_rows.invoice_number.readable = db.input_rows.invoice_number.writable = (
        False
    )
    db.input_rows.invoice_date.readable = db.input_rows.invoice_date.writable = False
    db.input_rows.due_date.readable = db.input_rows.due_date.writable = False

    form = Form(db.input_rows, record_id)
    if form.accepted:
        flash.set("record updated")
        redirect(URL("index"))
    return dict(form=form, message=message)


@action("index", method=["GET", "POST"])
@action("index/<action:path>", method=["GET", "POST"])
@action.uses(
    "form.html",
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def index(action=None):
    # breakpoint()
    message = ""
    # make the form
    db.input_rows.member.requires = IS_IN_DB(
        db, "contacts.id", "%(name)s", zero=T("choose one")
    )
    db.input_rows.account.requires = IS_IN_DB(
        db, "coa.id", "%(code)s %(description)s", zero=T("choose one")
    )
    db.input_rows.description_datetime.requires = IS_EMPTY_OR(IS_DATETIME())

    db.input_rows.invoice_number.readable = db.input_rows.invoice_number.writable = (
        False
    )
    db.input_rows.invoice_date.readable = db.input_rows.invoice_date.writable = False
    db.input_rows.due_date.readable = db.input_rows.due_date.writable = False

    form = Form(db.input_rows, keep_values=True)
    # add class = filterable to select fields, ready for js adjustments
    for field in form.structure.find("select"):
        field["_class"] = (field["_class"] or "") + " filterable"

    # make the rows
    rows = db(db.input_rows.down_loaded == False).select(orderby=~db.input_rows.id)

    # adjust account.description field to hold extra text fields - description_date_time, _text
    for row in rows:
        combine_description_fields(row)

    if form.accepted:
        flash.set("Record added", _class="error", sanitize=True)

    return dict(form=form, rows=rows, message=message)


def combine_description_fields(row):
    prefix = suffix = ""
    if row.description_datetime:
        prefix = str(row.description_datetime) + ":"
    if row.description_text:
        suffix = " - " + row.description_text
    total_description = " ".join([prefix, row.account.description, suffix])
    row.account.description = total_description


@action("coa", method=["POST", "GET"])
@action("coa/<path:path>", method=["POST", "GET"])
@action.uses(
    "grid.html",
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def coa(path=None):
    db_query = db.coa.id > 0
    grid = Grid(
        path,
        query=db_query,
        details=False,
        search_queries=[
            ["Search by Code", lambda val: db.coa.code.contains(val)],
            ["Search by Description", lambda val: db.coa.description.contains(val)],
        ],
        **GRID_DEFAULTS,
    )
    return dict(grid=grid)


@action("contacts", method=["POST", "GET"])
@action("contacts/<path:path>", method=["POST", "GET"])
@action.uses(
    "grid.html",
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def contacts(path=None):
    db_query = db.contacts.id > 0
    grid = Grid(
        path,
        query=db_query,
        details=False,
        left=[
            # db.clubs.on(db.contacts.club == db.clubs.id),
            db.clubs.on(db.contacts.club == db.clubs.id),
        ],
        search_queries=[
            ["Search by Sageid", lambda val: db.contacts.sageid.contains(val)],
            ["Search by Name", lambda val: db.contacts.name.contains(val)],
        ],
        **GRID_DEFAULTS,
    )
    return dict(grid=grid)


@action("batch_records_export", method=["GET"])
@action.uses(
    "download.html",
    db,
    session,
    flash,
    Inject(response=response),
)
def batch_records_export():
    stream = StringIO()
    content_type = "text/csv"
    filename = "batch_input.csv"
    response.headers["Content-Type"] = content_type
    response.headers["Content-disposition"] = f'attachment; filename="{filename}"'
    query = db.input_rows.down_loaded == False
    rows = db(query).select(orderby=~db.input_rows.id)
    rows_dict = []
    for row in rows:
        combine_description_fields(row)
        rows_dict.append(input_row_to_dict(row))
    field_names = [
        "ContactName",
        "Reference",
        "InvoiceNumber",
        "InvoiceDate",
        "DueDate",
        "Description",
        "Quantity",
        "UnitAmount",
        "AccountCode",
        "TaxType",
        "TrackingName1",
        "TrackingOption1",
        "BrandingTheme",
    ]

    writer = csv.DictWriter(stream, fieldnames=field_names)
    writer.writeheader()
    for rd in rows_dict:
        writer.writerow(rd)
    return locals()


##### grid doesn't look best ########
@action("batch_input", method=["POST", "GET"])
@action("batch_input/<path:path>", method=["POST", "GET"])
@action.uses(
    "grid.html",
    session,
    db,
    flash,
    Inject(
        make_title=make_title,
        make_navbar=make_navbar,
        menu_structure=menu_structure,
    ),
)
def batch_input(path=None):
    db_query = db.input_rows.id > 0
    grid = Grid(
        path,
        query=db_query,
        details=False,
        left=[
            db.contacts.on(db.input_rows.member == db.contacts.id),
            db.coa.on(db.input_rows.account == db.coa.id),
        ],
        **GRID_DEFAULTS,
    )

    return dict(grid=grid)
