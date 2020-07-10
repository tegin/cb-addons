# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestWebRegisterLogin(TransactionCase):
    def test_web_register_login(self):
        users_obj = self.env["res.users"]
        user_admin = users_obj.search([("login", "=", "admin")])
        logins_before = len(
            self.env["res.users.access.log"].search(
                [("create_uid", "=", user_admin.id)]
            )
        )
        # Login should be performed here but we dont want to commit
        # user_admin.sudo(user_admin)._login(self.env.cr.dbname, "admin", "admin")
        users_obj.sudo(user_admin.id).register_new_login()

        logins_after = len(
            self.env["res.users.access.log"].search(
                [("create_uid", "=", user_admin.id)]
            )
        )
        self.assertEqual(logins_after - logins_before, 1)

        user_admin.view_access_registers()
        user_admin.remote.view_access_registers()
