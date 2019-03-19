# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hash Search Document Attacher Queue',
    'summary': """
        Use queue as document attacher manager""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-ux',
    'depends': [
        'hash_search_document_scanner',
        'queue_job',
    ],
    'data': [
        'data/cron_data.xml',
        'data/config_parameter.xml',
    ],
    'external_dependencies': {
        'python': [
            'paramiko',
        ]
    }
}
