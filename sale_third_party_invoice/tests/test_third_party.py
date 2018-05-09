from odoo.tests.common import TransactionCase


class ThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref('base.main_company')
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
        sale_order.action_confirm()
        self.assertEqual('to invoice', sale_order.invoice_status)
        sale_order.action_invoice_create()
        self.assertEqual('invoiced', sale_order.invoice_status)
        self.assertEqual(sale_order.amount_total, 110)
        self.assertEqual(
            self.third_party_product,
            sale_order.invoice_ids.invoice_line_ids.product_id)
        self.assertEqual(sale_order.invoice_ids.amount_total, 12)
