from decimal import Decimal
from py4web import action, redirect, request, URL, Field
from py4web.utils.grid import Grid, Column

from py4web.utils.form import Form
from pydal.validators import *
from .common import (
    T,
    auth,
    authenticated,
    cache,
    db,
    flash,
    logger,
    session,
    unauthenticated,
    GRID_DEFAULTS,
)


@action("index", method=["GET", "POST"])
@action.uses("index.html")
def index():
    form = Form(db.input_rows)
    rows = db(db.input_rows).select()
    return dict(form=form, rows=rows)


@action("form", method=["GET", "POST"])
@action.uses("form.html")
def form():
    fields = [
        Field("contact_name", requires=IS_NOT_EMPTY(), length=25),
        Field("invoice_date", requires=IS_NOT_EMPTY(), type="date"),
        Field("invoice_number", requires=IS_NOT_EMPTY(), length=12),
    ]

    form = Form(fields)
    if form.accepted:
        print(form.vars)
    else:
        print(form)
    # redirect(URL("form"))
    return dict(form=form)

##### grid doesn't look best ########
@action("batch_input", method=["POST", "GET"])
@action("batch_input/<path:path>", method=["POST", "GET"])
@action.uses(
    "grid.html",
    session,
    db,
)
def batch_input(path=None):
    db_query = db.input_rows.id > 0
    grid = Grid(
        path,
        query=db_query,
        columns=[
            db.input_rows.invoice_number,
            db.input_rows.invoice_date,
            db.contacts.name,
        ],
        left=[db.contacts.on(db.input_rows.member == db.contacts.id)],
        headings=["Member", "Invoice Num", "Invoice Date"],
        **GRID_DEFAULTS,
    )

    return dict(grid=grid)

@action("create_form", method=["GET", "POST"])
@action.uses("form_basic.html", db)
def create_form():
    form = Form(db.input_rows)
    rows = db(db.input_rows).select()
    return dict(form=form, rows=rows)

@action("update_form/<input_row_id:int>", method=["GET", "POST"])
@action.uses("form_basic.html", db)
def update_form(input_row_id):
    form = Form(db.input_rows, input_row_id)
    rows = db(db.input_rows).select()
    return dict(form=form, rows=rows)
