from odoo.tests import common
from odoo.exceptions import UserError, ValidationError


@common.at_install(False)
@common.post_install(True)
class TestRuleField(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.model = "res.partner"
        self.model_id = self.env.ref("base.model_res_partner")
        self.rule = self.env["document.quick.access.rule"].create(
            {
                "model_id": self.model_id.id,
                "name": "PARTNER",
                "priority": 1,
                "barcode_format": "field",
                "field_name": "ref",
                "field_format": "^.*$",
            }
        )
        self.partner = self.env["res.partner"].create(
            {"name": "Partner test", "ref": "PARTNER_REF_TEST"}
        )

    def test_generation(self):
        code = self.partner.get_quick_access_code()
        self.assertTrue(code)
        self.assertEqual(code, self.partner.ref)
        result = self.env["document.quick.access.rule"].read_code(code)
        self.assertEqual(result, self.partner)

    def test_format_failure(self):
        self.rule.field_format = "^00.*$"
        code = self.partner.get_quick_access_code()
        with self.assertRaises(UserError):
            self.env["document.quick.access.rule"].read_code(code)

    def test_exception(self):
        with self.assertRaises(ValidationError):
            self.rule.field_name = False
