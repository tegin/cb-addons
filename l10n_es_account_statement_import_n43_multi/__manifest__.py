# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import N43 Multi Wizard",
    "summary": """
        Import n43 multi wizard""",
    "version": "14.0.1.0.0",
    "website": "https://github.com/tegin/cb-addons",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "depends": ["l10n_es_account_statement_import_n43", "edi_account_oca"],
    "data": [
        "security/ir.model.access.csv",
        "data/edi.xml",
        "wizards/account_statement_import_n43_multi.xml",
        "views/account_journal.xml",
        "views/edi_exchange_record.xml",
    ],
}
