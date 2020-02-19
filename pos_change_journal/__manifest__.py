# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "PoS Change Journal",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/eficent/cb-addons",
    "author": "Creu Blanca, Eficent",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds integration information",
    "depends": ["pos_close_approval"],
    "data": [
        "wizard/account_bank_statement_line_change_journal.xml",
        "views/account_bank_statement_line_views.xml",
    ],
}
