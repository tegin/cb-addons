# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CreditControlRun(models.Model):

    _inherit = "credit.control.run"

    def run_channel_action(self):
        result = super().run_channel_action()
        deferred_lines = self.line_ids.filtered(
            lambda x: x.state == "to_be_sent" and x.channel == "email_deferred"
        )
        if deferred_lines:
            comm_obj = self.env["credit.control.communication"]
            comm_obj._generate_comm_from_credit_lines(deferred_lines)
            deferred_lines.write({"state": "queued"})
        return result
