# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Qr Document Attacher',
    'summary': """
        Attach documents directly using QR""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': [
        'hash_search',
        'document',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/hash_missing_document_assign.xml',
        'views/hash_missing_document.xml',
        'data/config_parameter.xml',
    ],
    'external_dependencies': {
        'python': [
            'pyzbar',
            'pdf2image',
        ],
    },
    'demo': [
    ],
}
