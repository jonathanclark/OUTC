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
    message = ''
    if record:
        db(db.input_rows.id==record).delete()
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
    message = ''
    db.input_rows.invoice_number.readable = db.input_rows.invoice_number.writable = False
    db.input_rows.invoice_date.readable = db.input_rows.invoice_date.writable = False
    db.input_rows.due_date.readable = db.input_rows.due_date.writable = False

    form = Form(db.input_rows, record_id)
    if form.accepted:
        flash.set("record updated")
        redirect(URL('index'))
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
def form(action=None):
    message = ''
    #make the form
    db.input_rows.member.requires = IS_IN_DB(
        db, "contacts.id", "%(name)s", zero=T("choose one")
    )
    db.input_rows.account.requires = IS_IN_DB(
        db, "coa.id", "%(description)s", zero=T("choose one")
    )
    db.input_rows.invoice_number.readable = db.input_rows.invoice_number.writable = False
    db.input_rows.invoice_date.readable = db.input_rows.invoice_date.writable = False
    db.input_rows.due_date.readable = db.input_rows.due_date.writable = False

    form = Form(db.input_rows, keep_values=True)

    # make the rows
    rows = db(db.input_rows.down_loaded == False).select(orderby=~db.input_rows.id)
    # print(f"We have {len(rows)} rows in the database to deal with")
    # rows = [input_row_to_dict(r) for r in rows]
    # print(f"We now have {len(rows)} rows in the list of dicts to deal with")
    if action == 'clear':
        flash.set("The Clear all rows button doesn't do anything yet",
                  _class="error", sanitize = True)
    
    if form.accepted:
        flash.set("Record added", _class="error", sanitize=True)
        pass
    #print('here come rows')
    #for r in rows:
    #    print(r)
    return dict(form=form, rows=rows, message=message)


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
            #db.clubs.on(db.contacts.club == db.clubs.id),
            db.clubs.on(db.contacts.club == db.clubs.id),
        ],
        search_queries=[
            ["Search by Sageid", lambda val: db.contacts.sageid.contains(val)],
            ["Search by Name", lambda val: db.contacts.name.contains(val)],
        ],
        **GRID_DEFAULTS,
    )
    return dict(grid=grid)


@action("save_csv", method=["GET"])
@action.uses(
    db,
    session,
)
def save_csv():
    stream = StringIO()
    content_type = "text/csv"
    filename = "batch_input.csv"
    response.headers["Content-Type"] = content_type
    response.headers["Content-disposition"] = f'attachment; filename="{filename}"'
    rows = db(db.input_rows.down_loaded == False).select(orderby=~db.input_rows.id)
    rows_dict = [input_row_to_dict(r) for r in rows]
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
    ]

    writer = csv.DictWriter(stream, fieldnames=field_names)
    writer.writeheader()
    for rd in rows_dict:
        #print(rd)
        writer.writerow(rd)
    return XML(stream.getvalue())


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


