# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Intercompany journal',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'http://github.com/eficent/cb-addons',
    'summary': 'Creates inter company relations',
    'sequence': 30,
    'category': 'Accounting',
    'depends': ['mcfix_account'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/res_inter_company_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
