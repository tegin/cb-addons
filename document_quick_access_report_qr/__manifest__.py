# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Document Quick Access Report Qr",
    "description": """
        Add QR to models reports""",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
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
