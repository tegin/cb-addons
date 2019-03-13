# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Cb Invoice Print Label',
    'summary': """
        Module that allows you to print labels for referencing invoices""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca, Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': [
        'account',
        'remote_report_to_printer_label',
        'printer_zpl2',
        'hash_search_document_attacher',
    ],
    'data': [
        'data/account_invoice_label.xml',
        'views/invoice_supplier_form.xml',
    ],
    'demo': [
    ],
}
