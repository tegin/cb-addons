# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hash Search Account Invoice',
    'summary': """
        Allow to use hash search with invoices""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': [
        'account_banking_sepa_direct_debit',
        'hash_search',
        'web_qr',
    ],
    'data': [
        'reports/sepa_direct_debit_mandate.xml',
    ],
}
