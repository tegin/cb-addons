# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Creu Blanca Demo Database',
    'version': '10.0.1.0.0',
    'author': 'Eficent',
    'depends': [
        'workflow_plandefinition',
        'medical_request_group',
        'medical_careplan',
        'medical_encounter',
        'medical_encounter_careplan',
        'medical_procedure',
        'medical_insurance_sale',
        'medical_careplan_plandefinition',
        'medical_material',
        'medical_careplan_sale',
    ],
    'demo': [
        'demo_data/workflow_type.xml',
        'demo_data/product_category.xml',
        'demo_data/products.xml',
        'demo_data/activity_definition.xml',
        'demo_data/plan_definition.xml',
        'demo_data/sale_commission_formula.xml',
        'demo_data/practitioners.xml',
    ],
    'licence': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
