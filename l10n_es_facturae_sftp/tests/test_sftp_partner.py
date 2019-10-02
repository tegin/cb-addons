# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSftpIntegration(TransactionCase):
    def setUp(self):
        super(TestSftpIntegration, self).setUp()
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
                "ssh_server": "localhost",
                "ssh_port": 22,
                "ssh_name": "ssh_name",
                "ssh_pass": "ssh_pass",
                "ssh_folder": "ssh_folder",
                "ssh_report_id": self.browse_ref(
                    "account.account_invoices_without_payment"
                ).id,
                "invoice_integration_method_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref(
                                "l10n_es_facturae_sftp.integration_sftp"
                            ).id
                        ],
                    )
                ],
            }
        )

    def test_constrain_01(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_server = False

    def test_constrain_02(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_port = False

    def test_constrain_03(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_name = False

    def test_constrain_04(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_pass = False

    def test_constrain_05(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_folder = False

    def test_constrain_06(self):
        with self.assertRaises(ValidationError):
            self.partner.ssh_report_id = False
