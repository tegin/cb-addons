# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentRegistryTestCase


class EDIBackendTestCase(
    EDIBackendCommonComponentRegistryTestCase, common.TransactionCase
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._load_module_components(cls, "component_event")
        cls._load_module_components(cls, "edi")
        cls._load_module_components(cls, "storage")
        cls._load_module_components(cls, "edi_account_oca")
        cls._load_module_components(cls, "edi_storage_oca")
        cls._load_module_components(cls, "edi_account_storage")
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Test tax",
                "amount_type": "percent",
                "amount": 21,
                "type_tax_use": "sale",
            }
        )
        cls.storage = cls.env["fs.storage"].create(
            {"name": "storage", "protocol": "odoofs", "code": "demo.fs.storage"}
        )
        cls.backend = cls.env["edi.backend"].create(
            {
                "name": "Demo Backend",
                "backend_type_id": cls.env.ref("edi_account_storage.backend_type").id,
                "storage_id": cls.storage.id,
            }
        )
        cls.exchange_type = cls.env["edi.exchange.type"].create(
            {
                "name": "Storage backend demo",
                "backend_type_id": cls.env.ref("edi_account_storage.backend_type").id,
                "backend_id": cls.backend.id,
                "code": "edi_account_storage_partner",
                "direction": "output",
            }
        )
        cls.env["edi.exchange.template.output"].create(
            {
                "name": "Storage backend demo",
                "backend_type_id": cls.env.ref("edi_account_storage.backend_type").id,
                "backend_id": cls.backend.id,
                "type_id": cls.exchange_type.id,
                "code": "edi_account_storage_partner_template",
                "output_type": "pdf",
                "generator": "report",
                "report_id": cls.env.ref("account.account_invoices").id,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Cliente de prueba",
                "street": "C/ Ejemplo, 13",
                "zip": "13700",
                "city": "Tomelloso",
                "country_id": cls.env.ref("base.es").id,
                "vat": "ES05680675C",
                "account_invoice_storage_exchange_type_id": cls.exchange_type.id,
            }
        )
        main_company = cls.env.ref("base.main_company")
        main_company.vat = "ESA12345674"
        main_company.partner_id.country_id = cls.env.ref("base.uk")
        cls.sale_journal = cls.env["account.journal"].create(
            {
                "name": "Sale journal",
                "code": "SALE_TEST",
                "type": "sale",
                "company_id": main_company.id,
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "company_id": main_company.id,
                "name": "Facturae Product account",
                "code": "testproduct",
                "account_type": "income",
            }
        )
        cls.move = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "journal_id": cls.sale_journal.id,
                "invoice_date": "2016-03-12",
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.env.ref("product.product_delivery_02").id,
                            "account_id": cls.account.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, cls.tax.ids)],
                        },
                    )
                ],
            }
        )
        cls.move.flush_recordset()

    def test_send(self):
        self.move.with_context(
            force_edi_send=True, _edi_send_break_on_error=True
        ).action_post()
        self.assertTrue(self.move.exchange_record_ids)
        self.assertEqual(
            self.move.exchange_record_ids.edi_exchange_state, "output_sent"
        )
