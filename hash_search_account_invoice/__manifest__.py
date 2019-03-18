# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hash Search Account Invoice',
    'summary': """
        Allow to use hash search with invoices""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': [
        'account',
        'hash_search',
    ],
    'data': [
        'data/account_invoice_label.xml',
    ],
}
