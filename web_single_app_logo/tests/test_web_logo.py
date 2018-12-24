import base64
from mock import patch

from odoo import tools
from odoo.http import Response
from odoo.tests.common import HttpCase, post_install, at_install
from ..controllers.main import MulticompanyLogo


class FakeRequest(object):
    endpoint = False

    def __init__(self, env):
        self.env = env


class FakeResponse(object):
    data = ''
    headers = {}

    def __init__(self, data, filename=False, mtime=False):
        self.data = data
        self.headers = dict({
            'filename': filename,
            'mtime': mtime
        })


def fake_response(data, filename=False, mtime=False):
    return Response(data.getvalue(), direct_passthrough=True)


@post_install(True)
@at_install(False)
class TestWebSingleAppLogo(HttpCase):
    def test_logo(self):
        data = self.url_open('/app_logo.png')
        self.assertEqual(data.headers['Content-Type'], 'image/png')

    def test_with_mock(self):
        image = tools.file_open(
            "logo.png", mode="rb", subdir="addons/web_single_app_logo/tests"
        ).read()
        settings = self.env['res.config.settings'].create({})
        settings.single_app_logo = base64.b64encode(image)
        settings.execute()
        with patch('odoo.http.request', new=FakeRequest(self.env)):
            with patch('odoo.http.send_file', new=fake_response):
                data = MulticompanyLogo.app_logo(self)
        import logging
        logging.info(data)
        self.assertEqual(data.data, image)
