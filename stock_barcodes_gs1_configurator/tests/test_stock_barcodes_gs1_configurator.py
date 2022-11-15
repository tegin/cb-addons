# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

from odoo.addons.stock_barcodes.tests import test_stock_barcodes


@common.tagged("post_install", "-at_install")
class TestStockBarcodesGS1Configurator(test_stock_barcodes.TestStockBarcodes):
    def setUp(self):
        super().setUp()
        # Barcode for packaging and lot
        self.gs1_barcode_01_product = "0119501101530000"
        self.gs1_barcode_01_lot = "1714070410AB-123"
        self.gs1_barcode_01 = self.gs1_barcode_01_product + self.gs1_barcode_01_lot
        # Barcode for product and quantities
        self.gs1_barcode_02_product = "0207010001234567"
        self.gs1_barcode_02_lot = "150410183724"
        self.gs1_barcode_02 = self.gs1_barcode_02_product + self.gs1_barcode_02_lot

        self.product_template = self.env["product.template"].create(
            {
                "name": "Product Template Test",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.product = self.product_template.product_variant_id

    def test_action_check_packaging(self):
        action = self.product_template.action_check_packaging()
        self.assertTrue(action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "barcode.action")
        self.assertEqual(action["context"]["default_res_id"], self.product.id)

    def test_read_package_gs1_action(self):
        res = self.product.read_package_gs1_action(self.gs1_barcode_01)
        self.assertTrue(res["res_id"])
        self.assertEqual(res["res_model"], "product.packaging")
        self.assertEqual(res["name"], "Product Packagings")
        res = self.product.read_package_gs1_action(False)
        self.assertEqual(res["res_model"], "barcode.action")
        self.assertEqual(res["name"], "Search Package")
        self.assertTrue(
            res["context"]["default_status"],
            "Something went wrong. Please, try again.",
        )

    def test_process_gs1_package_barcode_01(self):
        package_first_scan = self.product.process_gs1_package_barcode(
            self.gs1_barcode_01
        )
        self.assertTrue(package_first_scan)
        self.assertEqual(package_first_scan.product_id, self.product)
        self.assertEqual("01" + package_first_scan.barcode, self.gs1_barcode_01_product)
        package_second_scan = self.product.process_gs1_package_barcode(
            self.gs1_barcode_01
        )
        self.assertTrue(package_second_scan)
        self.assertEqual(package_second_scan.product_id, self.product)
        self.assertEqual(
            "01" + package_second_scan.barcode, self.gs1_barcode_01_product
        )
        self.assertEqual(package_first_scan, package_second_scan)

    def test_process_gs1_package_barcode_02(self):
        package_first_scan = self.product.process_gs1_package_barcode(
            self.gs1_barcode_02_product
        )
        self.assertTrue(package_first_scan)
        self.assertEqual(package_first_scan.product_id, self.product)
        self.assertEqual("02" + package_first_scan.barcode, self.gs1_barcode_02_product)
        package_second_scan = self.product.process_gs1_package_barcode(
            self.gs1_barcode_02
        )
        self.assertTrue(package_second_scan)
        self.assertEqual(package_second_scan.product_id, self.product)
        self.assertEqual(
            "02" + package_second_scan.barcode, self.gs1_barcode_02_product
        )
        self.assertEqual(package_first_scan, package_second_scan)
