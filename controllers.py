import csv
import datetime
from decimal import Decimal
from io import StringIO

from py4web import URL, Field, Flash, abort, action, redirect, request, response
from py4web.utils.form import Form
from py4web.utils.grid import Column, Grid

# from py4web.utils.factories import Inject
from pydal.validators import *
from yatl.helpers import *
from yatl.helpers import A

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


@action("old-index")
@action.uses("index.html", flash, auth, T)
def index():
    flash.set("Hello World", _class="error", sanitize=True)
    user = auth.get_user()
    message = T("Hello {first_name}").format(**user) if user else T("Hello")
    return dict(message=message)


@action("index", method=["GET", "POST"])
@action("index/<action:path>", method=["GET", "POST"])
@action.uses(
    "form.html",
    session,
    db,
    flash,
)
def form(action=None):
    db.input_rows.member.requires = IS_IN_DB(
        db, "contacts.id", "%(name)s", zero=T("choose one")
    )
    db.input_rows.account.requires = IS_IN_DB(
        db, "coa.id", "%(description)s", zero=T("choose one")
    )
    if action=='clear':
        print("Action is clear")

    form = Form(db.input_rows, keep_values=True)
    rows = db(db.input_rows.down_loaded == False).select(orderby=~db.input_rows.id)
    # print(f"We have {len(rows)} rows in the database to deal with")
    rows = [input_row_to_dict(r) for r in rows]
    # print(f"We now have {len(rows)} rows in the list of dicts to deal with")
    message = ""
    if form.accepted:
        flash = {
            "message": "Input line has been added",
            "class": "info",
        }
        # print(form.vars)
        pass
    else:
        # print("error")
        pass
    return dict(form=form, rows=rows, message=message)


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
        details=False,
        left=[
            db.contacts.on(db.input_rows.member == db.contacts.id),
            db.coa.on(db.input_rows.account == db.coa.id),
        ],
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


# ####################################
# htmx demo follows


@action("htmx_form_demo", method=["GET", "POST"])
@action.uses("htmx_form_demo.html")
def htmx_form_demo():
    return dict(timestamp=datetime.datetime.now())


@action("htmx_list", method=["GET", "POST"])
@action.uses("htmx_list.html", db)
def htmx_list():
    input_rows = db(db.input_rows.id > 0).select()
    return dict(input_rows=input_rows)


@action("htmx_form/<record_id>", method=["GET", "POST"])
@action.uses("htmx_form.html", db)
def htmx_form(record_id=None):
    attrs = {
        "_hx-post": URL("htmx_form/%s" % record_id),
        "_hx-target": "#htmx-form-demo",
    }
    form = Form(db.input_rows, record=db.input_rows(record_id), **attrs)
    if form.accepted:
        redirect(URL("htmx_list"))

    cancel_attrs = {
        "_hx-get": URL("htmx_list"),
        "_hx-target": "#htmx-form-demo",
    }
    form.param.sidecar.append(A("Cancel", **cancel_attrs))

    return dict(form=form)


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
        writer.writerow(rd)
    return XML(stream.getvalue())
