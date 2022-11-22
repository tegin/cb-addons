# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pos Manual Order",
    "summary": """
        Add Orders manually on a PoS Session""",
    "version": "14.0.1.0.0",
    "website": "https://github.com/tegin/cb-addons",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/pos_session_add_order.xml",
        "views/pos_session.xml",
    ],
}
