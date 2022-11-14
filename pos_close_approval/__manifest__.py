# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "PoS Close approval",
    "version": "13.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/tegin/cb-addons",
    "author": "Creu Blanca, Eficent",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds integration information",
    "depends": ["pos_multiple_sessions", "pos_session_pay_invoice"],
    "post_load": "post_load_hook",
    "data": [
        "wizard/bank_statement_account.xml",
        "views/pos_config_views.xml",
        "views/pos_session_views.xml",
        "views/bank_statement_views.xml",
        "security/point_of_sale_security.xml",
    ],
}
