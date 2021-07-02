# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Report",
    "summary": """
        Improve Picking report""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_report.xml",
        "reports/report_picking_operations.xml",
    ],
}
