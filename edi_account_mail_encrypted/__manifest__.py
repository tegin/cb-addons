# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Integration Email Encrypted",
    "summary": """
        Send invoices through emails as an integration method""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "https://github.com/tegin/cb-addons",
    "depends": ["edi_account_mail"],
    "data": [
        "security/security.xml",
        "wizards/res_view_value.xml",
        "wizards/res_encrypt_value.xml",
        "views/res_partner_view.xml",
    ],
    "external_dependencies": {"python": ["PyPDF2"]},
}
