# Copyright 2021 Creu Blanca.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestStockRequest(common.TransactionCase):
    def setUp(self):
        super(TestStockRequest, self).setUp()

        self.company_1 = self.env["res.company"].create(
            {"name": "Test Company 1"}
        )
        self.partner_1 = self.env["res.partner"].create(
            {"name": "Partner Test 1"}
        )
        self.warehouse_1 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse Test 1",
                "code": "WH1",
                "company_id": self.company_1.id,
                "partner_id": self.partner_1.id,
            }
        )
        self.location_1 = self.env["stock.location"].create(
            {
                "name": "Test Location 1",
                "location_id": self.warehouse_1.view_location_id.id,
                "usage": "internal",
                "company_id": self.company_1.id,
            }
        )
        self.partner_2 = self.env["res.partner"].create(
            {"name": "Partner Test 2"}
        )
        self.company_2 = self.env["res.company"].create(
            {"name": "Test Company 2"}
        )
        self.warehouse_2 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse Test 2",
                "code": "WH2",
                "company_id": self.company_2.id,
                "partner_id": self.partner_2.id,
            }
        )
        self.location_2 = self.env["stock.location"].create(
            {
                "name": "Test Location 2",
                "location_id": self.warehouse_2.view_location_id.id,
                "usage": "internal",
                "company_id": self.company_2.id,
            }
        )

        self.product_1 = self.env["product.product"].create(
            {
                "name": "Product test 1",
                "default_code": "PT1",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        lines = [
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 3,
            },
            {
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 5,
            },
        ]
        self.template = self.env["stock.request.template"].create(
            {
                "name": "Stock Request Template Test",
                "warehouse_id": self.warehouse_1.id,
                "location_id": self.location_1.id,
                "company_id": self.company_1.id,
                "template_line_ids": [(0, 0, line) for line in lines],
            }
        )
        self.request_order = self.env["stock.request.order"].create(
            {
                "name": "Stock Request Order Test",
                "company_id": self.company_1.id,
                "warehouse_id": self.warehouse_1.id,
                "location_id": self.location_1.id,
            }
        )

    def test_stock_request_template_onchange_warehouse_id(self):
        self.template.warehouse_id = self.warehouse_2.id
        self.template.onchange_warehouse_id()
        self.assertEqual(
            self.template.location_id.get_warehouse(), self.warehouse_2
        )
        self.assertEqual(self.template.company_id, self.company_2)

    def test_stock_request_template_onchange_company_id(self):
        self.template.company_id = self.company_2.id
        self.template.onchange_company_id()
        self.assertEqual(self.template.warehouse_id.company_id, self.company_2)
        self.assertEqual(self.template.location_id.company_id, self.company_2)

    def test_stock_request_template_onchange_location_id(self):
        self.template.location_id = self.location_2.id
        self.template.onchange_location_id()
        self.assertEqual(
            self.template.location_id.get_warehouse(), self.warehouse_2
        )
        self.assertEqual(self.template.company_id, self.company_2)

    def test_stock_request_template_line_check_product_quantity(self):
        with self.assertRaises(ValidationError):
            self.env["stock.request.template.line"].create(
                {
                    "template_id": self.template.id,
                    "product_id": self.product_1.id,
                    "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                    "product_uom_qty": 0,
                }
            )

    def test_stock_request_template_line_onchange_product_id(self):
        line = self.env["stock.request.template.line"].create(
            {
                "template_id": self.template.id,
                "product_id": self.product_1.id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1,
            }
        )
        res = line.onchange_product_id()
        self.assertEqual(
            res["domain"]["product_uom_id"][0],
            ("category_id", "=", self.product_1.uom_id.category_id.id),
        )
        line.product_id = None
        res = line.onchange_product_id()
        self.assertFalse(res["domain"]["product_uom_id"])

    def test_stock_request_order_apply_template(self):
        self.assertEqual(len(self.request_order.stock_request_ids), 0)
        wizard = self.env["stock.request.order.template"].create(
            {
                "template_id": self.template.id,
                "order_id": self.request_order.id,
            }
        )
        wizard.apply_template()
        self.assertEqual(len(self.request_order.stock_request_ids), 2)
        self.assertEqual(
            self.template.warehouse_id, self.request_order.warehouse_id
        )
        self.assertEqual(
            self.template.template_line_ids[0].product_id,
            self.request_order.stock_request_ids[0].product_id,
        )
        self.assertEqual(
            self.template.template_line_ids[0].product_uom_qty,
            self.request_order.stock_request_ids[0].product_uom_qty,
        )
