# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'L10n ES IVA Soportado No Deducible',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'depends': [
        'l10n_es',
        'l10n_es_aeat_mod303',
        'l10n_es_aeat_mod390',
        'l10n_es_aeat_mod349',
        'l10n_es_vat_book',
    ],
    'data': [
        'data/account_account_template_common_data.xml',
        'data/account_tax_data.xml',
        'data/tax_code_map_mod303_data.xml',
        'data/tax_code_map_mod390_data.xml',
        'data/aeat_349_map_data.xml',
        'data/map_taxes_vat_book.xml',
    ],
    'website': 'https://github.com/Eficent/cb-addons',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
