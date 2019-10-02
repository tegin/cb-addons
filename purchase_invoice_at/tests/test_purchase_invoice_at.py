# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.fields import Datetime
from odoo.exceptions import ValidationError


class TestPurchaseExternal(TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier = self.env["res.partner"].create(
            {"name": "Supplier", "supplier": True}
        )
        self.payor = self.env["res.partner"].create({"name": "Payor"})
        self.product = self.env["product.product"].create(
            {"type": "consu", "name": "Product"}
        )
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.supplier.id,
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
                        },
                    )
                ],
            }
        )

    def test_order_company_constrain(self):
        company = self.env["res.company"].create({"name": "Company"})
        self.payor.company_id = company
        with self.assertRaises(ValidationError):
            self.po.partner_to_invoice_id = self.payor

    def test_order_company_onchange_no_company(self):
        company = self.env["res.company"].create({"name": "Company"})
        po = self.env["purchase.order"].new(
            {
                "partner_id": self.supplier.id,
                "partner_to_invoice_id": self.payor.id,
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
                        },
                    )
                ],
            }
        )
        self.payor.company_id = False
        self.assertTrue(po.partner_to_invoice_id)
        po.update({"company_id": company.id})
        po._onchange_company_partner_to_invoice()
        self.assertTrue(po.partner_to_invoice_id)

    def test_order_company_onchange(self):
        company = self.env["res.company"].create({"name": "Company"})
        po = self.env["purchase.order"].new(
            {
                "partner_id": self.supplier.id,
                "partner_to_invoice_id": self.payor.id,
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
                        },
                    )
                ],
            }
        )
        self.assertTrue(po.partner_to_invoice_id)
        po.update({"company_id": company.id})
        po._onchange_company_partner_to_invoice()
        self.assertFalse(po.partner_to_invoice_id)

    def test_order_counter(self):
        self.assertEqual(0, self.payor.invoiced_purchase_count)
        self.po.partner_to_invoice_id = self.payor
        self.assertEqual(1, self.payor.invoiced_purchase_count)

    def test_consumable_no_external(self):
        self.po.button_confirm()
        self.assertEqual(0, self.po.order_line.qty_invoiced)
        self.assertEqual(self.po.invoice_status, "no")
        for line in self.po.picking_ids.move_lines:
            line.quantity_done = line.product_uom_qty
        self.po.picking_ids.button_validate()
        self.assertEqual(self.po.invoice_status, "to invoice")
        self.assertEqual(0, self.po.order_line.qty_invoiced)

    def test_consumable_external(self):
        self.po.partner_to_invoice_id = self.payor
        self.assertEqual(0, self.po.order_line.qty_invoiced)
        self.assertEqual(self.po.invoice_status, "no")
        self.po.button_confirm()
        self.assertEqual(0, self.po.order_line.qty_invoiced)
        self.assertEqual(self.po.invoice_status, "no")
        for line in self.po.picking_ids.move_lines:
            line.quantity_done = line.product_uom_qty
        self.po.picking_ids.button_validate()
        self.assertEqual(self.po.invoice_status, "no")
        self.assertEqual(1, self.po.order_line.qty_invoiced)

    def test_service_no_external(self):
        self.product.type = "service"
        self.assertEqual(0, self.po.order_line.qty_invoiced)
        self.assertEqual(self.po.invoice_status, "no")
        self.po.button_confirm()
        self.assertEqual(self.po.invoice_status, "to invoice")
        self.assertEqual(0, self.po.order_line.qty_invoiced)

    def test_service_external(self):
        self.po.partner_to_invoice_id = self.payor
        self.product.type = "service"
        self.assertEqual(0, self.po.order_line.qty_invoiced)
        self.assertEqual(self.po.invoice_status, "no")
        self.po.button_confirm()
        self.assertEqual(self.po.invoice_status, "no")
        self.assertEqual(1, self.po.order_line.qty_invoiced)
