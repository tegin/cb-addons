from odoo import fields
from odoo.tests.common import TransactionCase
import dateutil.relativedelta


class TestSaleCommission(TransactionCase):

    def setUp(self):
        super(TestSaleCommission, self).setUp()
        self.commission_model = self.env['sale.commission']
        self.commission_net_invoice = self.commission_model.create({
            'name': '10% fixed commission (Net amount) - Invoice Based',
            'fix_qty': 10.0,
            'amount_base_type': 'net_amount',
        })
        self.res_partner_model = self.env['res.partner']
        self.partner = self.res_partner_model.create({
            'name': 'Partner'
        })
        self.partner.write({'supplier': False, 'agent': False})
        self.sale_order_model = self.env['sale.order']
        self.advance_inv_model = self.env['sale.advance.payment.inv']
        self.settle_model = self.env['sale.commission.settlement']
        self.make_settle_model = self.env['sale.commission.make.settle']
        self.make_inv_model = self.env['sale.commission.make.invoice']
        self.product = self.env['product.product'].create({
            'name': 'Product',
            'type': 'service',
            'invoice_policy': 'order',
        })
        self.journal = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1
        )
        self.agent_1 = self.res_partner_model.create({
            'name': 'Test Agent - Monthly',
            'agent': True,
            'settlement': 'monthly',
            'lang': 'en_US',
        })
        self.agent_2 = self.res_partner_model.create({
            'name': 'Test Agent 2 - Monthly',
            'agent': True,
            'settlement': 'monthly',
            'lang': 'en_US',
        })

    def _create_sale_order(self, agent, commission):
        return self.sale_order_model.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'product_uom': self.ref('product.product_uom_unit'),
                'price_unit': self.product.lst_price,
                'agents': [(0, 0, {
                    'agent': agent.id,
                    'commission': commission.id
                })]
            })]
        })

    def test_change(self):
        sale_order = self._create_sale_order(
            self.agent_1, self.commission_net_invoice)

        sale_order.action_confirm()
        self.assertEqual(len(sale_order.invoice_ids), 0)
        payment = self.advance_inv_model.create({
            'advance_payment_method': 'all',
        })
        context = {"active_model": 'sale.order',
                   "active_ids": [sale_order.id],
                   "active_id": sale_order.id}
        payment.with_context(context).create_invoices()
        self.assertNotEqual(len(sale_order.invoice_ids), 0)
        sale_order.invoice_ids.action_invoice_open()
        line = sale_order.invoice_ids.invoice_line_ids
        agent_line = line.agents
        self.assertTrue(agent_line)
        self.assertTrue(agent_line.can_cancel)
        self.assertEqual(agent_line.agent, self.agent_1)
        self.assertFalse(agent_line.is_cancel)
        action = self.env['account.invoice.agent.change'].create({
            'agent_line': agent_line.id,
            'agent': self.agent_1.id,
        })
        action.run()
        line.refresh()
        self.assertEqual(len(line.agents), 1)
        self.assertEqual(agent_line, line.agents)
        self.assertEqual(agent_line.agent, self.agent_1)
        action = self.env['account.invoice.agent.change'].create({
            'agent_line': agent_line.id,
            'agent': self.agent_2.id,
        })
        action.run()
        line.refresh()
        agent_line.refresh()
        self.assertEqual(len(line.agents), 1)
        self.assertEqual(agent_line.agent, self.agent_2)
        agent_line = line.agents
        wizard = self.make_settle_model.create(
            {'date_to': (fields.Datetime.from_string(fields.Datetime.now()) +
                         dateutil.relativedelta.relativedelta(months=1))})
        wizard.action_settle()
        action = self.env['account.invoice.agent.change'].create({
            'agent_line': agent_line.id,
            'agent': self.agent_1.id,
        })
        action.run()
        line.refresh()
        self.assertEqual(len(line.agents), 3)
        self.assertIn(agent_line.id, line.agents.ids)
        agent_line.refresh()
        self.assertFalse(agent_line.can_cancel)
        self.assertEqual(agent_line.agent, self.agent_2)
        self.assertTrue(line.agents.filtered(lambda r: r.is_cancel))
        self.assertTrue(line.agents.filtered(
            lambda r: r.agent == self.agent_1))
