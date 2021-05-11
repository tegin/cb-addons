# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.storage_backend.tests.common import CommonCase
from odoo.exceptions import ValidationError


class TestStorageIntegration(CommonCase):
    def setUp(self):
        super(TestStorageIntegration, self).setUp()
        self.state = self.env["res.country.state"].create(
            {
                "name": "Ciudad Real",
                "code": "13",
                "country_id": self.ref("base.es"),
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "NAME",
                "street": "C/ Ejemplo, 13",
                "zip": "13700",
                "city": "Tomelloso",
                "state_id": self.state.id,
                "country_id": self.ref("base.es"),
                "vat": "ES05680675C",
                "facturae": True,
                "organo_gestor": "1",
                "unidad_tramitadora": "1",
                "oficina_contable": "1",
                "account_integration_report_id": self.browse_ref(
                    "account.account_invoices_without_payment"
                ).id,
                "account_integration_storage_id": self.backend.id,
                "account_integration_filename_pattern": "Invoice_{invoice.number}.pdf",
                "invoice_integration_method_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref(
                                "l10n_es_facturae_storage.integration_storage"
                            ).id
                        ],
                    )
                ],
            }
        )

    def test_constrain_01(self):
        with self.assertRaises(ValidationError):
            self.partner.account_integration_report_id = False

    def test_constrain_02(self):
        with self.assertRaises(ValidationError):
            self.partner.account_integration_storage_id = False

    def test_constrain_03(self):
        with self.assertRaises(ValidationError):
            self.partner.account_integration_filename_pattern = False
