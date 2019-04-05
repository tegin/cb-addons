# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': ' CB Extended Leave Days Computation',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Allows to take into account in leave days the'
               'computation of rest days and the possibility of'
               'counting holidays by full dates or hours.',
    'author': 'iDT LABS, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/holidays_security.xml',
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
    ],
    'installable': True,
}
