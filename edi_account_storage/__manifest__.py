# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n Es Facturae Storage",
    "summary": """
        Summary""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "development_status": "Alpha",
    "depends": ["edi_account_oca", "edi_storage_oca", "edi_exchange_template_oca"],
    "data": [
        "data/edi_data.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
    ],
}
