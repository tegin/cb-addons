from odoo.tests.common import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestCustomInfoForm(HttpCase):
    def setUp(self):
        super().setUp()
        self.category = self.env["custom.info.category"].create(
            {"name": "Category", "sequence": 100}
        )
        self.template = self.env["custom.info.template"].create(
            {
                "name": "demo template",
                "model_id": self.env.ref(
                    "custom_info_form.model_custom_info_form"
                ).id,
                "property_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "First field",
                            "sequence": 1,
                            "widget": "text",
                            "category_id": self.category.id,
                        },
                    )
                ],
            }
        )
        self.user = self.env["res.users"].create(
            {
                "name": "DEMO USER",
                "login": "test_demo_user",
                "password": "test_demo_user",
                "groups_id": [
                    (4, self.env.ref("base.group_user").id),
                    (
                        4,
                        self.env.ref(
                            "custom_info_form.group_custom_info_form_manager"
                        ).id,
                    ),
                ],
            }
        )

    def test_custom_info(self):
        self.authenticate(self.user.login, self.user.login)
        self.url_open("/form/fill_form?template_id=%s" % self.template.id)
        forms = self.env["custom.info.form"].search(
            [("custom_info_template_id", "=", self.template.id)]
        )
        self.assertTrue(forms)
        self.assertFalse(forms.custom_info_ids.value)

    def test_custom_info_compute(self):
        self.template.property_ids.write({"compute_form_value": "user.name"})
        self.authenticate(self.user.login, self.user.login)
        self.url_open("/form/fill_form?template_id=%s" % self.template.id)
        forms = self.env["custom.info.form"].search(
            [("custom_info_template_id", "=", self.template.id)]
        )
        self.assertTrue(forms)
        self.assertEqual(forms.custom_info_ids.value, self.user.name)
