#! python
"""
    To build the menu structure for the site

    Structure is [triples]
    Triples are - href which is usually a word but could be a full URL
                - text to display in anchor link
                - sub-menu
    See menu_structure below. Note you cannot have sub-menu of sub-menu.
    Must handle site/target e.g. 127.0.0.1/contact as well as site/tgaa/target
    (Remember that if app is _default, appid is not required)

"""

from yatl.helpers import *
from py4web import URL
from .settings import APP_NAME

# hard-coded variables
nav_bg_colour = "has-background-blue"
# nav_bg_colour = ""


def DOC(document, vars=None):
    return URL("static", "documents", document)


menu_structure = [
    ('index', 'Main Input screen'),
    ('maintenance', 'Edit other tables',
        [ 
         ('contacts', 'Member'),
         ('coa', 'Nominal accounts'),
         ]
     ),
    ]


def make_navbar(menu_structure):
    """
    Build the navbar for the page we are on.

    Can work out the page we're on from request. Be careful about
    _default app e.g.
        given url ip:port/test/about r.app_name = test, r.path = /test/about
        given url ip:port/about r.app_name = _default, r.path = /about

    """

    # make components to go into navbar
    main_navbar_id = "main-navbar"
    span = SPAN(**{"_aria-hidden": "true"})
    hamburger = A(
        span,
        span,
        span,
        **{
            "_role": "button",
            "_class": "navbar-burger",
            "_aria-label": "menu",
            "_aria-expanded": "false",
            "_data-target": main_navbar_id,
        }
    )

    content = DIV(_class="navbar")
    # first item goes in start_content, rest go in end_content
    # It's a Bulma thing
    target = content
    for item in menu_structure or []:
        if not item[2:]:
            target.append(A(item[1], _href=URL(item[0]), _class="navbar-item has-background-blue"))
        else:
            sub_list = DIV(_class="navbar-dropdown")
            for sub_item in item[2]:
                sub_list.append(
                    (A(sub_item[1], _href=URL(sub_item[0]), _class="navbar-item has-background-blue"))
                )
            group = DIV(
                A(item[1], _class="navbar-link has-background-blue"),
                sub_list,
                _class="navbar-item has-dropdown is-hoverable",
            )

            target.append(group)

    navbar = TAG.nav(
        DIV(
            hamburger,
            DIV(content, **{"_id": main_navbar_id, "_class": "navbar-menu is_active"}),
        ),
        _class=" ".join(["navbar", nav_bg_colour, "is-fixed-top"]),
        _role="navigation",
        **{"_aria-label": "main navigation"}
    )

    return navbar


def make_title(target):
    return " - ".join(["Trap Grounds Allotment Association", target.removeprefix("/")])
