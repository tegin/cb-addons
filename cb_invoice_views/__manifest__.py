# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cb Invoice Views',
    'summary': """
        Modify invoice views css""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': [
        'web',
        'account',
        'medical_administration',
    ],
    'data': [
        'views/theme_default_templates.xml'
    ],
}
