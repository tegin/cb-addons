# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


class TestManualOrder(TestPointOfSaleCommon):
    def setUp(self):
        super().setUp()
        self.product3 = self.env["product.product"].create(
            {"name": "TEST PRODUCT", "type": "service", "taxes_id": []}
        )
        self.product4 = self.env["product.product"].create(
            {"name": "TEST PRODUCT 4", "type": "service", "taxes_id": []}
        )

    def test_manual_order_excluded(self):
        session = self.pos_order_session0
        self.assertTrue(session.config_id.pricelist_id)
        self.assertFalse(session.order_ids)
        wizard = self.env["pos.session.add.order"].create(
            {
                "session_id": session.id,
                "price": 10,
                "product_id": self.product4.id,
                "journal_id": session.journal_ids[0].id,
            }
        )
        self.assertTrue(wizard)
        wizard.run()
        self.assertTrue(session.order_ids)
        self.assertEqual(1, len(session.order_ids))
        self.assertEqual(10, session.order_ids.lines.price_subtotal)

    def test_manual_order_included(self):
        session = self.pos_order_session0
        self.assertTrue(session.config_id.pricelist_id)
        self.assertFalse(session.order_ids)
        wizard = self.env["pos.session.add.order"].create(
            {
                "session_id": session.id,
                "price": 10,
                "product_id": self.product3.id,
                "journal_id": session.journal_ids[0].id,
            }
        )
        self.assertTrue(wizard)
        wizard.run()
        self.assertTrue(session.order_ids)
        self.assertEqual(1, len(session.order_ids))
        self.assertEqual(10, session.order_ids.lines.price_subtotal_incl)

    def test_onchange_journal(self):
        session = self.pos_order_session0
        self.product3.lst_price = 10
        with self.env.do_in_onchange():
            wizard = self.env["pos.session.add.order"].new({})
            self.assertFalse(wizard.journal_ids)
            wizard.session_id = session
            self.assertTrue(wizard.journal_ids)

    def test_onchange_product(self):
        session = self.pos_order_session0
        self.product3.lst_price = 10
        with self.env.do_in_onchange():
            wizard = self.env["pos.session.add.order"].new(
                {"session_id": session.id, "qty": 1}
            )
            self.assertEqual(0, wizard.price)
            self.assertEqual(0, wizard.amount_total)
            wizard.product_id = self.product3
            wizard._onchange_product()
            self.assertNotEqual(0, wizard.price)
            self.assertNotEqual(0, wizard.amount_total)
