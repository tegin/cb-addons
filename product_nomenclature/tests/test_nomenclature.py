from odoo.tests.common import TransactionCase


class TestNomenclature(TransactionCase):
    def setUp(self):
        super().setUp()
        self.nomenclature = self.env["product.nomenclature"].create(
            {"name": "Nomenclature", "code": "nomenclature"}
        )
        self.product = self.env["product.product"].create(
            {"name": "Product", "default_code": "prd"}
        )

    def test_onchange(self):
        item = self.env["product.nomenclature.product"].new(
            {
                "nomenclature_id": self.nomenclature.id,
                "product_id": self.product.id,
            }
        )
        item._onchange_product()
        self.assertEqual(self.product.name, item.name)
        self.assertEqual(self.product.default_code, item.code)

    def test_view(self):
        item = self.env["product.nomenclature.product"].create(
            {
                "nomenclature_id": self.nomenclature.id,
                "name": "TESt",
                "code": "tests",
                "product_id": self.product.id,
            }
        )
        action = self.nomenclature.action_view_items()
        items = self.env["product.nomenclature.product"].search(
            action["domain"]
        )
        self.assertIn(item.id, items.ids)
