# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Sale third party invoice',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'http://github.com/eficent/cb-addons',
    'summary': 'Creates inter company relations',
    'sequence': 30,
    'category': 'Sale',
    'depends': [
        'sale',
        'mcfix_sale',
    ],
    'license': 'LGPL-3',
    'data': [
        'views/sale_order_views.xml',
        'views/partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
