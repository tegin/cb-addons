# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Credit Control Deferred",
    "summary": """
        Defferred credit control mails""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["account_credit_control"],
    "data": [
        "views/credit_control_communication.xml",
        "views/res_partner.xml",
    ],
    "post_init_hook": "post_init_hook",
}
