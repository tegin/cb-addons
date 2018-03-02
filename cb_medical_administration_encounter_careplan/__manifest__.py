# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'CB Medical Administration Encounter Careplan',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'category': 'Medical',
    'depends': [
        'medical_administration_encounter_careplan',
    ],
    'data': [
        'views/medical_careplan_views.xml',
        'views/medical_encounter_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
