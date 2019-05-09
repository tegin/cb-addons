# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'L10n Es Facturae Sftp',
    'summary': """
        Summary""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': [
        'invoice_integration_email_encrypted',
    ],
    'data': [
        'data/sftp_data.xml',
        'views/res_partner.xml',
    ],
}
