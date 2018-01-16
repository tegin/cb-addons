# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account_journal_inter_company.tests import common


class TestInterCompanyCashInvoice(common.TestInterCompany):

    def setUp(self):
        super(TestInterCompanyCashInvoice, self).setUp()
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'type': 'service',
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Partner',
            'customer': True,
            'supplier': True,
        })
        self.user_type = self.browse_ref('account.data_account_type_revenue')

    def create_invoice(self, company, inv_type):
        journal = self.env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'sale')
        ], limit=1)
        invoice = self.env['account.invoice'].create({
            'company_id': company.id,
            'type': inv_type,
            'partner_id': self.partner.id,
            'journal_id': journal.id,
        })
        account = self.env['account.account'].search([
            ('company_id', '=', company.id),
            ('user_type_id', '=', self.user_type.id)
        ], limit=1)
        self.env['account.invoice.line'].create({
            'invoice_id': invoice.id,
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': 100,
            'name': self.product.name,
            'account_id': account.id,
        })
        invoice.with_context(force_company=company.id).action_invoice_open()
        return invoice

    def test_cash_invoice(self):
        self.create_inter_company(self.company_1, self.company_2)
        journal_1 = self.env['account.journal'].search(
            [('company_id', '=', self.company_1.id)], limit=1)
        statement = self.env['account.bank.statement'].create({
            'name': 'Statement',
            'journal_id': journal_1.id
        })
        invoice_out = self.create_invoice(self.company_2, 'out_invoice')
        invoice_in = self.create_invoice(self.company_2, 'in_invoice')

        in_invoice = self.env['cash.invoice.in'].with_context(
            active_ids=statement.ids, active_model=statement._name
        ).create({
            'invoice_id': invoice_in.id,
            'amount': 100.0
        })
        in_invoice.run()
        out_invoice = self.env['cash.invoice.out'].with_context(
            active_ids=statement.ids, active_model=statement._name
        ).create({
            'invoice_id': invoice_out.id,
            'amount': 100.0
        })
        out_invoice.run()
        statement.balance_end_real = statement.balance_start
        statement.check_confirm_bank()
        self.assertEqual(invoice_out.residual, 0.)
        self.assertEqual(invoice_in.residual, 0.)
