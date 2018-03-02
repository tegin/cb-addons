# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Cash payments between intercompanies',
    'version': '11.0.1.0.0',
    'author': 'Eficent, Creu Blanca, Odoo Community Association (OCA)',
    'website': 'http://github.com/eficent/cb-addons',
    'summary': 'Payment of invoices to another company',
    'sequence': 30,
    'category': 'Accounting',
    'depends': [
        'account',
        'account_cash_invoice',
        'account_journal_inter_company'
    ],
    'license': 'LGPL-3',
    'data': [
        'views/account_bank_statement_line.xml',
        'wizard/cash_invoice_in.xml',
        'wizard/cash_invoice_out.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
