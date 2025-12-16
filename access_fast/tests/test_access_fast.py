# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import HttpCase


class TestAccessFast(HttpCase):
    def setUp(self):
        super().setUp()
        self.access_fast = self.env["ir.access.fast"].create(
            {
                "name": "RP",
                "model_id": self.env.ref("base.model_res_partner").id,
                "field_id": self.env.ref("base.field_res_partner__name").id,
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "partner",
                "email": "test@example.com",
            }
        )

    def test_unauthenticated(self):

        result = self.url_open("/access_fast/RP/partner", allow_redirects=False)

        self.assertEqual(result.status_code, 303)
        self.assertIn("/web/login", result.headers["Location"])

    def test_wrong_action(self):

        self.authenticate("admin", "admin")

        result = self.url_open("/access_fast/AA/partner")

        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.text, "Action not found")

    def test_wrong_record(self):

        self.authenticate("admin", "admin")

        result = self.url_open("/access_fast/RP/falsePartner")

        self.assertEqual(result.status_code, 404)
        self.assertEqual(result.text, "Record not found")

    def test_access_fast(self):

        self.authenticate("admin", "admin")

        result = self.url_open("/access_fast/RP/partner", allow_redirects=False)

        self.assertEqual(result.status_code, 303)
