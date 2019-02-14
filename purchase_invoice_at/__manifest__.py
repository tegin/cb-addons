# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "Purchase invoice at",
    'summary': "Short subtitle phrase",
    'author': "Creu Blanca, Odoo Community Association (OCA)",
    'license': "AGPL-3",
    'website': "www.creublanca.es",
    'category': 'Uncategorized',
    'version': '11.0.1.0.0',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_views.xml',
        'views/purchase_order_report.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [],
}