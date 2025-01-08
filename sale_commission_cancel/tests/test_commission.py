from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Models
        cls.commission_model = cls.env["commission"]
        cls.res_partner_model = cls.env["res.partner"]
        cls.sale_order_model = cls.env["sale.order"]
        cls.advance_inv_model = cls.env["sale.advance.payment.inv"]
        cls.settle_model = cls.env["commission.settlement"]
        cls.make_settle_model = cls.env["commission.make.settle"]
        cls.make_inv_model = cls.env["commission.make.invoice"]

        # Commission setup
        cls.commission_net_invoice = cls.commission_model.create(
            {
                "name": "10% fixed commission (Net amount) - Invoice Based",
                "fix_qty": 10.0,
                "amount_base_type": "net_amount",
            }
        )

        # Company setup
        cls.company = cls.env.ref("base.main_company")

        # Partner setup
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.partner.write({"agent": False})

        # Product setup
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "service",
                "invoice_policy": "order",
            }
        )

        # Journal setup
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "purchase")], limit=1
        )

        # Agents setup
        cls.agent_1 = cls.res_partner_model.create(
            {
                "name": "Test Agent - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": 1,
            }
        )
        cls.agent_2 = cls.res_partner_model.create(
            {
                "name": "Test Agent 2 - Monthly",
                "agent": True,
                "settlement": "monthly",
                "lang": "en_US",
                "commission_id": 1,
            }
        )

    def _create_sale_order(self, agent, commission):
        order_form = Form(self.sale_order_model)
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        order.order_line.agent_ids = [
            (0, 0, {"agent_id": agent.id, "commission_id": commission.id})
        ]
        return order

    def test_change(self):
        sale_order = self._create_sale_order(self.agent_1, self.commission_net_invoice)
        sale_order.action_confirm()
        self.assertEqual(len(sale_order.invoice_ids), 0)

        payment = self.advance_inv_model.create(
            {
                "advance_payment_method": "delivered",
                "sale_order_ids": [(4, sale_order.id)],
            }
        )
        context = {
            "active_model": "sale.order",
            "active_ids": [sale_order.id],
            "active_id": sale_order.id,
        }
        payment.with_context(**context).create_invoices()
        self.assertNotEqual(len(sale_order.invoice_ids), 0)

        sale_order.invoice_ids.action_post()
        line = sale_order.invoice_ids.invoice_line_ids
        agent_line = line.agent_ids
        self.assertTrue(agent_line)
        self.assertTrue(agent_line.can_cancel)
        self.assertEqual(agent_line.agent_id, self.agent_1)
        self.assertFalse(agent_line.is_cancel)
        action = self.env["account.invoice.agent.change"].create(
            {"agent_line": agent_line.id, "agent": self.agent_1.id}
        )
        action.run()
        line.invalidate_recordset()
        self.assertEqual(len(line.agent_ids), 1)
        self.assertEqual(agent_line, line.agent_ids)
        self.assertEqual(agent_line.agent_id, self.agent_1)

        action = self.env["account.invoice.agent.change"].create(
            {"agent_line": agent_line.id, "agent": self.agent_2.id}
        )
        action.run()
        line.invalidate_recordset()
        agent_line.invalidate_recordset()
        self.assertEqual(len(line.agent_ids), 1)
        self.assertEqual(agent_line.agent_id, self.agent_2)
        agent_line = line.agent_ids

        wizard = self.make_settle_model.create(
            {
                "date_to": (
                    fields.Datetime.from_string(fields.Datetime.now())
                    + relativedelta(months=1)
                ),
                "settlement_type": "sale_invoice",
            }
        )
        wizard.action_settle()

        action = self.env["account.invoice.agent.change"].create(
            {"agent_line": agent_line.id, "agent": self.agent_1.id}
        )
        action.run()
        line.invalidate_recordset()
        self.assertEqual(len(line.agent_ids), 3)
        self.assertIn(agent_line.id, line.agent_ids.ids)
        agent_line.invalidate_recordset()
        self.assertFalse(agent_line.can_cancel)
        self.assertEqual(agent_line.agent_id, self.agent_2)
        self.assertTrue(line.agent_ids.filtered(lambda r: r.is_cancel))
        self.assertTrue(line.agent_ids.filtered(lambda r: r.agent_id == self.agent_1))
