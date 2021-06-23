# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "L10n Es Facturae Storage",
    "summary": """
        Summary""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "website": "www.creublanca.es",
    "development_status": "Alpha",
    "depends": [
        "l10n_es_facturae",
        "edi_account",
        "edi_storage",
        "edi_exchange_template",
    ],
    # TODO: Remove L10n_es_facturae after migration
    "data": [
        "data/edi_data.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
    ],
}
