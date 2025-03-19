import base64

from odoo import tools
from odoo.tests.common import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebSingleAppLogo(HttpCase):
    def test_logo(self):
        data = self.url_open("/app_logo.png")
        self.assertEqual(data.headers["Content-Type"], "image/png")

    def test_with_mock(self):
        image = tools.file_open(
            "addons/web_single_app_logo/tests/logo.png", mode="rb"
        ).read()
        settings = self.env["res.config.settings"].create({})
        settings.single_app_logo = base64.b64encode(image)
        settings.execute()
        data = self.url_open("/app_logo.png")
        self.assertEqual(data.content, image)
