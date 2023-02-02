# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class BaseRemote(models.Model):

    _inherit = "res.remote"

    def view_access_registers(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "web_register_login.res_users_access_log_act_window"
        )
        action["domain"] = [("remote_id", "=", self.id)]
        return action
