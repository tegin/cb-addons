# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common

from odoo.addons.component.tests.common import SavepointComponentRegistryCase


class EDIBackendTestCase(SavepointComponentRegistryCase, common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        self = cls

        self._load_module_components(self, "component_event")
        self._load_module_components(self, "edi")
        self._load_module_components(self, "storage")
        self._load_module_components(self, "edi_account")
        self._load_module_components(self, "edi_storage")
        self._load_module_components(self, "edi_account_storage")
        self.tax = self.env["account.tax"].create(
            {
                "name": "Test tax",
                "amount_type": "percent",
                "amount": 21,
                "type_tax_use": "sale",
            }
        )
        self.storage = self.env["storage.backend"].create(
            {"name": "storage", "backend_type": "filesystem"}
        )
        self.backend = self.env["edi.backend"].create(
            {
                "name": "Demo Backend",
                "backend_type_id": self.env.ref("edi_account_storage.backend_type").id,
                "storage_id": self.storage.id,
            }
        )
        self.exchange_type = self.env["edi.exchange.type"].create(
            {
                "name": "Storage backend demo",
                "backend_type_id": self.env.ref("edi_account_storage.backend_type").id,
                "backend_id": self.backend.id,
                "code": "edi_account_storage_partner",
                "direction": "output",
            }
        )
        self.env["edi.exchange.template.output"].create(
            {
                "name": "Storage backend demo",
                "backend_type_id": self.env.ref("edi_account_storage.backend_type").id,
                "backend_id": self.backend.id,
                "type_id": self.exchange_type.id,
                "code": "edi_account_storage_partner_template",
                "output_type": "pdf",
                "generator": "report",
                "report_id": self.env.ref("account.account_invoices").id,
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Cliente de prueba",
                "street": "C/ Ejemplo, 13",
                "zip": "13700",
                "city": "Tomelloso",
                "country_id": self.env.ref("base.es").id,
                "vat": "ES05680675C",
                "account_invoice_storage_exchange_type_id": self.exchange_type.id,
            }
        )
        main_company = self.env.ref("base.main_company")
        main_company.vat = "ESA12345674"
        main_company.partner_id.country_id = self.env.ref("base.uk")
        self.sale_journal = self.env["account.journal"].create(
            {
                "name": "Sale journal",
                "code": "SALE_TEST",
                "type": "sale",
                "company_id": main_company.id,
            }
        )
        self.account = self.env["account.account"].create(
            {
                "company_id": main_company.id,
                "name": "Facturae Product account",
                "code": "facturae_product",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.move = self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                # "account_id": self.partner.property_account_receivable_id.id,
                "journal_id": self.sale_journal.id,
                "invoice_date": "2016-03-12",
                "type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref(
                                "product.product_delivery_02"
                            ).id,
                            "account_id": self.account.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        self.move.refresh()

    def test_send(self):
        self.move.with_context(
            force_edi_send=True, _edi_send_break_on_error=True
        ).post()
        self.assertTrue(self.move.exchange_record_ids)
        self.assertEqual(
            self.move.exchange_record_ids.edi_exchange_state, "output_sent"
        )
