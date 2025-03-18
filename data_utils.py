"""
Utils for database
Run from py4web dir (i.e. above apps dir)

Will include:
    export all tables to csv
    import all tables from csv
    load_clubs      load clubs from program text
    load_coa        load coa from the file Chart
    load_contacts   load contacts from

Format of csv for export / import is
TABLE tablename
Header row of field names
Data rows
two blank lines
etc.

So to change a table name, just export all, edit csv to change table names, import

How to run:
    python -c "from apps.OUTC.data_utils import export_all_tables; export_all_tables('all_tables.csv')"
    python -c "from apps.OUTC.data_utils import import_all_tables; import_all_tables('all_tables.csv')"
    python -c "from apps.OUTC.data_utils import delete_all_tables; delete_all_tables('all_tables.csv')"
"""

import csv

member_types = {
    "Associates": "",
    "Country": "Unicorn",
    "Ex-OUTC": "",
    "Former Member": "",
    "Friend Of Court": "",
    "Full Booking": "Unicorn",
    "Full Senior": "Unicorn",
    "Groups OUTC": "",
    "Groups UNICORN": "",
    "Honorary": "",
    "Junior": "OUTC",
    "Newsletter": "",
    "Oxford University Student": "OUTC",
    "Professional": "",
    "Student (Other)": "OUTC",
}


from apps.OUTC.common import db, groups


def load_clubs():
    """
    python -c "from apps.OUTC.data_utils import load_clubs; load_clubs()"
    """
    for club_name in ["Unicorn", "OUTC"]:
        if db(db.clubs.name == club_name).count() == 0:
            db.clubs.insert(name=club_name)

    db.commit()

    print("There are now %d lines in clubs" % db(db.clubs.id > 0).count())


def load_contacts(input_file="jc_active_members.csv"):
    """
    python -c 'from apps.OUTC.data_utils import load_contacts; load_contacts()'
    """
    with open(input_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            # breakpoint()
            if member_types[row[3]] in ["OUTC", "Unicorn"]:
                clubs_id = db(db.clubs.name == member_types[row[3]]).select().first().id
                db.contacts.insert(
                    sageid=row[0],
                    name=" ".join([row[1], row[2]]),
                    club=clubs_id,
                )
    db.commit()

    print("There are now %d lines in contacts" % db(db.contacts.id > 0).count())


def load_coa(input_file="ChartOfAccountsOTC.csv"):
    """
    python -c 'from apps.OUTC.data_utils import load_coa; load_coa()'
    """
    with open(input_file, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            # breakpoint()
            # print(row)
            key = db.coa.insert(
                code=row[0],
                description=row[1],
                type=row[2],
                tax_code=row[3],
            )
            # print(key)
    db.commit()

    print("There are now %d lines in the coa" % db(db.coa.id > 0).count())


def clean_all_tables():
    print("Clean all tables")
    for t in db.tables():
        db[t].truncate()
        db.commit()


def load_all_tables():
    print("Load all tables")
    load_clubs()
    load_contacts()
    load_coa()


def init_auth_user():
    db.auth_user.bulk_insert(
        [
            {
                "email": "ads@whatho.net",
            },
            {
                "email": "jc@whatho.net",
            },
            {
                "email": "lettings@outc.org.uk",
            },
        ]
    )


def export_all_tables(csv_file):
    with open(csv_file, "w", encoding="utf-8", newline="") as dumpfile:
        db.export_to_csv_file(dumpfile)


def import_all_tables(csv_file):
    with open(csv_file, "r", encoding="utf-8", newline="") as dumpfile:
        db.import_from_csv_file(dumpfile)
        db.commit()


# #################################
# utility functions


def input_row_to_dict(row):
    """covert row to r and return r

    r is just a dict, used in form and when writing csv
    """

    r = dict()
    r["ContactName"] = row.member.name
    r["Reference"] = row.member.sageid
    r["InvoiceNumber"] = row.invoice_number
    r["InvoiceDate"] = row.invoice_date
    r["DueDate"] = row.due_date
    if row.extra_description:
        r["Description"] = ", ".join(
            [
                row.account.description,
                row.extra_description,
            ]
        )
    else:
        r["Description"] = row.account.description
    r["Quantity"] = row.quantity
    r["UnitAmount"] = row.price
    r["AccountCode"] = row.account.code
    r["TaxType"] = row.account.tax_code
    r["TrackingName1"] = "Club"
    r["TrackingOption1"] = row.member.club.name
    return r
