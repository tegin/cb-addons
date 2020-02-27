# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Quick Access Label",
    "summary": """
        Allows to print labels from Document Quick Access records""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-ux",
    "depends": [
        "document_quick_access",
        "printer_zpl2",
        "remote_report_to_printer_label",
    ],
    "data": ["views/document_quick_access_rule.xml"],
}
