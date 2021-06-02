# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Cash Box management",
    "version": "12.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "website": "http://github.com/eficent/cb-addons",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Accounting",
    "depends": ["account"],
    "license": "AGPL-3",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_safe_box_move.xml",
        "wizard/wizard_safe_box_count.xml",
        "wizard/wizard_safe_box_move_external.xml",
        "views/safe_box_menu.xml",
        "views/safe_box_group_views.xml",
        "views/safe_box_views.xml",
        "views/safe_box_coin_views.xml",
        "views/safe_box_move_views.xml",
        "views/account_account_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
