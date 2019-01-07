# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Pos Manual Order',
    'summary': """
        Add Orders manually on a PoS Session""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'wizards/pos_session_add_order.xml',
        'views/pos_session.xml',
    ],
    'demo': [
    ],
}
