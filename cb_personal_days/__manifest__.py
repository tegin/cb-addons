# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cb Personal Days',
    'description': """
        Modulo para organizar los dias libres personales""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca, Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
    ],
}
