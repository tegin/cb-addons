# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale Commission Cancel',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'http://github.com/eficent/cb-addons',
    'summary': 'Creates inter company relations',
    'sequence': 30,
    'category': 'Sale',
    'depends': [
        'sale_commission',
    ],
    'license': 'LGPL-3',
    'data': [
        'wizard/account_invoice_agent_change_view.xml',
        'views/account_invoice_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
