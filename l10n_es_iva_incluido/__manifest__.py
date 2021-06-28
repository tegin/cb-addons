# Copyright 2020 Creu Blanca
# Copyright 2020 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "L10n ES IVA Incluido",
    "version": "13.0.1.0.0",
    "author": "ForgeFlow, Creu Blanca",
    "depends": [
        "l10n_es",
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_mod390",
        "l10n_es_aeat_mod349",
        "l10n_es_aeat_mod347",
        "l10n_es_vat_book",
        "l10n_es_facturae",
    ],
    "data": [
        "data/account_tax_data.xml",
        "data/tax_code_map_mod303_data.xml",
        "data/tax_code_map_mod347_data.xml",
        "data/tax_code_map_mod390_data.xml",
        "data/map_taxes_vat_book.xml",
    ],
    "website": "https://github.com/Eficent/cb-addons",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
