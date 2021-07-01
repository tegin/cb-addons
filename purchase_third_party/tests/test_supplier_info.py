# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestPurchaseThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tp_partner = self.env["res.partner"].create(
            {"name": "Test third party partner"}
        )
        self.supplier = self.env["res.partner"].create(
            {"name": "Test supplier"}
        )
        self.uom_id = self.env.ref("uom.product_uom_unit").id
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
        self.supplier_info = self.mto_product.seller_ids

    def test_check_third_party_company(self):
        company_1 = self.env["res.company"].create({"name": "Comp1"})
        company_2 = self.env["res.company"].create({"name": "Comp2"})
        with self.assertRaises(UserError):
            self.supplier_info.company_id = company_1
            self.tp_partner.write({"company_id": company_1.id})
            self.supplier.write({"company_id": company_2.id})

    def test_check_third_party_price(self):
        with self.assertRaises(ValidationError):
            self.mto_product.write(
                {
                    "seller_ids": [
                        (
                            0,
                            0,
                            {
                                "name": self.supplier.id,
                                "third_party_partner_id": self.tp_partner.id,
                                "third_party_price": False,
                                "price": 7,
                            },
                        )
                    ]
                }
            )

    def test_check_third_party_tmpl(self):
        self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "third_party_partner_id": self.tp_partner.id,
                "third_party_price": 5,
                "price": 7,
                "product_tmpl_id": self.mto_product.product_tmpl_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["product.supplierinfo"].create(
                {
                    "name": self.supplier.id,
                    "third_party_partner_id": self.supplier.id,
                    "third_party_price": 5,
                    "price": 7,
                    "product_tmpl_id": self.mto_product.product_tmpl_id.id,
                }
            )

    def test_check_third_party(self):
        self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "third_party_partner_id": self.tp_partner.id,
                "third_party_price": 5,
                "price": 7,
                "product_id": self.mto_product.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["product.supplierinfo"].create(
                {
                    "name": self.supplier.id,
                    "third_party_partner_id": self.supplier.id,
                    "third_party_price": 5,
                    "price": 7,
                    "product_id": self.mto_product.id,
                }
            )

    def test_onchange_third_party_partner(self):
        self.mto_product.seller_ids.write({"third_party_partner_id": False})
        self.mto_product.seller_ids._onchange_third_party_partner()
        self.assertEqual(self.mto_product.seller_ids.third_party_price, False)
