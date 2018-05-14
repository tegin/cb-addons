from odoo.tests.common import TransactionCase


class ThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref('base.main_company')
        self.company.write({
            'default_third_party_customer_account_id': self.env[
                'account.account'].create({
                    'company_id': self.company.id,
                    'code': 'ThirdPartyCust',
                    'name': 'Third party customer account',
                    'user_type_id': self.browse_ref(
                        'account.data_account_type_revenue').id,
                    'reconcile': True,
                }).id,
            'default_third_party_supplier_account_id': self.env[
                'account.account'].create({
                    'company_id': self.company.id,
                    'code': 'ThirdPartySupp',
                    'name': 'Third party supplier account',
                    'user_type_id': self.browse_ref(
                        'account.data_account_type_revenue').id,
                    'reconcile': True,
                }).id,
        })
        self.supplier = self.env['res.partner'].create({
            'name': 'supplier',
            'supplier': True,
            'third_party_sequence_id': self.env['ir.sequence'].create({
                'name': 'supplier third party sequence',
            }).id
        })
        self.customer = self.env['res.partner'].create({
            'name': 'Customer',
            'customer': True,
        })
        self.product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Product'
        })
        self.third_party_taxes = self.env['account.tax'].create({
            'company_id': self.company.id,
            'name': 'Supplier Tax',
            'amount': 20,
            'type_tax_use': 'sale',
        })
        self.tax = self.env['account.tax'].create({
            'company_id': self.company.id,
            'name': 'Tax',
            'amount': 10,
            'type_tax_use': 'sale',
        })
        self.third_party_product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Third party product',
            'taxes_id': [(6, 0, self.third_party_taxes.ids)],
        })
        self.product = self.env['product.product'].create({
            'type': 'service',
            'name': 'Product',
            'taxes_id': [(6, 0, self.tax.ids)],
        })

    def test_third_party(self):
        sale_order = self.env['sale.order'].create({
            'company_id': self.company.id,
            'partner_id': self.customer.id,
            'third_party_order': True,
            'third_party_partner_id': self.supplier.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'third_party_product_id': self.third_party_product.id,
                'product_uom': self.product.uom_id.id,
                'product_uom_qty': 1,
                'price_unit': 100,
                'third_party_price': 10,
                'tax_id': [(6, 0, self.tax.ids)]
            })]
        })
        self.assertEqual(0, sale_order.invoice_count)
        self.assertEqual('no', sale_order.invoice_status)
        self.assertFalse(sale_order.third_party_move_id)
        sale_order.action_confirm()
        self.assertEqual('no', sale_order.invoice_status)
        self.assertEqual(len(sale_order.third_party_order_ids), 1)
        third_party_order = sale_order.third_party_order_ids[0]
        self.assertEqual(third_party_order.partner_id,
                         sale_order.third_party_partner_id)
        self.assertEqual(sale_order.amount_total, 110)
        self.assertTrue(sale_order.third_party_move_id)
        self.assertEqual(sale_order.third_party_customer_amount, 110)
        self.assertEqual(sale_order.third_party_customer_state, 'pending')
        self.assertEqual(sale_order.state, 'done')
        journal = self.env['account.journal'].search(
            [('company_id', '=', self.company.id)], limit=1)
        statement = self.env['account.bank.statement'].create({
            'name': 'Statement',
            'journal_id': journal.id
        })
        wizard = self.env['cash.third.party.sale'].with_context(
            active_ids=statement.ids, active_model=statement._name
        ).create({
            'sale_order_id': sale_order.id,
            'amount': 0
        })
        wizard._onchange_sale_order()
        self.assertEqual(wizard.amount, sale_order.amount_total)
        wizard.amount = 100
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_amount, 10)
        self.assertEqual(sale_order.third_party_customer_state, 'pending')
        statement = self.env['account.bank.statement'].create({
            'name': 'Statement',
            'journal_id': journal.id
        })
        wizard = self.env['cash.third.party.sale'].with_context(
            active_ids=statement.ids, active_model=statement._name
        ).create({
            'sale_order_id': sale_order.id,
            'amount': 0
        })
        wizard._onchange_sale_order()
        self.assertEqual(wizard.amount, sale_order.third_party_customer_amount)
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_state, 'payed')
