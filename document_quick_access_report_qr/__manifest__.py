# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Quick Access Report Qr",
    "summary": """
        Add QR to models reports""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "depends": [
        "document_quick_access",
        "account_banking_sepa_direct_debit",
        "report_qr",
        "sale",
    ],
    "data": [
        "report/report_invoice.xml",
        "report/sale_report_templates.xml",
        "report/sepa_direct_debit_mandate.xml",
    ],
}
