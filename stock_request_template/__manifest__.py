# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Request Template",
    "summary": """
        Create Templates for Stock Request Orders""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["stock_request"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_request_order_template.xml",
        "views/stock_request_template.xml",
        "views/stock_request_order.xml",
    ],
}
