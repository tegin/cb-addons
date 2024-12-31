# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.tests.common import TransactionCase


class TestWebRegisterLogin(TransactionCase):
    def setUp(self):
        super().setUp()
        self.remote_addr = "127.0.0.1"
        http.request = type(
            "obj",
            (object,),
            {
                "env": self.env,
                "cr": self.env.cr,
                "db": self.env.cr.dbname,
                "endpoint": type("obj", (object,), {"routing": []}),
                "httprequest": type(
                    "obj",
                    (object,),
                    {"remote_addr": self.remote_addr},
                ),
            },
        )

    def test_web_register_login(self):
        users_obj = self.env["res.users"]
        user_admin = self.env.user
        logins_before = len(
            self.env["res.users.access.log"].search(
                [("create_uid", "=", user_admin.id)]
            )
        )
        # Login should be performed here but we dont want to commit
        # user_admin.sudo(user_admin)._login(self.env.cr.dbname, "admin", "admin")
        users_obj.with_user(user_admin.id).register_new_login()

        logins_after = len(
            self.env["res.users.access.log"].search(
                [("create_uid", "=", user_admin.id)]
            )
        )
        self.assertEqual(logins_after - logins_before, 1)

        action = user_admin.remote.view_access_registers()
        self.assertEqual(
            self.env["res.users.access.log"].search(
                [("create_uid", "=", user_admin.id)]
            ),
            self.env[action["res_model"]].search(action["domain"]),
        )
        remote = self.env["res.remote"].search([("ip", "=", self.remote_addr)])
        action = remote.view_access_registers()
        self.assertEqual(
            self.env["res.users.access.log"].search([("remote_id", "=", remote.id)]),
            self.env[action["res_model"]].search(action["domain"]),
        )
