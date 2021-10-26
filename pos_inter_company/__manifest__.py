# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Cash payments between intercompanies",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "website": "http://github.com/eficent/cb-addons",
    "summary": "Payment of invoices to another company",
    "sequence": 30,
    "category": "Accounting",
    "depends": [
        "pos_session_pay_invoice",
        "account_journal_inter_company",
        "mcfix_point_of_sale",
        "pos_close_approval",
    ],
    "license": "AGPL-3",
    "data": [
        "views/account_bank_statement_line.xml",
        "views/pos_session.xml",
        "wizard/cash_invoice_in.xml",
        "wizard/cash_invoice_out.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
