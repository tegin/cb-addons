# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.fields import Datetime


class TestPurchaseThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tp_partner = self.env["res.partner"].create(
            {"name": "Test third party partner"}
        )
        self.supplier = self.env["res.partner"].create(
            {"name": "Test supplier"}
        )

        self.uom_id = self.env.ref("product.product_uom_unit").id
        self.mto_product = self.env["product.product"].create(
            {
                "name": "Test buy product",
                "type": "product",
                "uom_id": self.uom_id,
                "uom_po_id": self.uom_id,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.supplier.id,
                            "third_party_partner_id": self.tp_partner.id,
                            "third_party_price": 5,
                            "price": 7,
                        },
                    )
                ],
            }
        )

    def test_procurement_third_party(self):
        route = self.env.ref("purchase.route_warehouse0_buy")
        rule = self.env["procurement.rule"].search(
            [("route_id", "=", route.id)], limit=1
        )
        rule._run_buy(
            product_id=self.mto_product,
            product_qty=1,
            product_uom=self.mto_product.uom_id,
            location_id=self.env["stock.location"].search([], limit=1),
            name="Procurement order test",
            origin="Test",
            values={
                "company_id": self.env.user.company_id,
                "date_planned": Datetime.now(),
            },
        )
        purchase = self.env["purchase.order"].search([("origin", "=", "Test")])
        self.assertEqual(purchase.third_party_partner_id, self.tp_partner)
        self.assertEqual(purchase.order_line.third_party_price_unit, 5)
