# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web Session Management',
    'description': """
        Session management""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'depends': [
        'base_sparse_field'
    ],
    'data': [
        'wizards/res_users_sessions_wizard.xml',
        'views/http_session_user.xml',
    ],
    'demo': [
    ],
}
