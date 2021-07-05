# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Import N43 Multi Wizard",
    "summary": """
        Import n43 multi wizard""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca",
    "depends": ["l10n_es_account_bank_statement_import_n43", "edi_account"],
    "data": [
        "data/edi.xml",
        "wizards/account_bank_statement_import_n43_multi.xml",
        "views/account_journal.xml",
    ],
}
