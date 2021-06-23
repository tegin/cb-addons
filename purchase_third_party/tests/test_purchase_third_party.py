# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestPurchaseThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref("base.main_company")
        self.vendor = self.env["res.partner"].create({"name": "Supplier"})
        self.tp_partner = self.env["res.partner"].create(
            {"name": "Third Party Partner"}
        )
        self.tax = self.env["account.tax"].create(
            {
                "company_id": self.company.id,
                "name": "Tax",
                "amount": 21,
                "type_tax_use": "sale",
            }
        )
        self.product = self.env["product.product"].create(
            {"type": "consu", "name": "Product"}
        )

    def test_no_third_party(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "price_unit": 10,
                            "product_qty": 1,
                            "product_uom": self.product.uom_po_id.id,
                            "date_planned": Datetime.now(),
                            "taxes_id": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(po.order_line.price_subtotal, 10)
        self.assertEqual(po.order_line.price_tax, 2.1)
        self.assertEqual(po.order_line.price_total, 12.1)

    def test_third_party(self):
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.vendor.id,
                "third_party_order": True,
                "third_party_partner_id": self.tp_partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": self.product.name,
                            "price_unit": 10,
                            "third_party_price_unit": 7,
                            "product_qty": 1,
                            "product_uom": self.product.uom_po_id.id,
                            "date_planned": Datetime.now(),
                            "taxes_id": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(po.order_line.price_subtotal, 10)
        self.assertEqual(po.order_line.price_tax, 2.1)
        self.assertEqual(po.order_line.price_total, 12.1)
        self.assertEqual(po.order_line.third_party_price_subtotal, 7)
        self.assertEqual(po.order_line.third_party_price_tax, 1.47)
        self.assertEqual(po.order_line.third_party_price_total, 8.47)
        self.assertEqual(po.tp_amount_untaxed, 7)
        self.assertEqual(po.tp_amount_tax, 1.47)
        self.assertEqual(po.tp_amount_total, 8.47)
        po.with_context(third_party_send=True).action_rfq_send()
