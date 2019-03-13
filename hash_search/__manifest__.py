# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hash Search',
    'summary': """
        Summary""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': [
        'barcode_action',
    ],
    'data': [
        'views/assets_backend.xml',
        'wizards/barcode_action.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/hash_search_launcher.xml'
    ]
}
