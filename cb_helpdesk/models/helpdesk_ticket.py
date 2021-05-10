# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HelpdeskTicket(models.Model):

    _inherit = "helpdesk.ticket"

    partner_phone = fields.Char()

    def send_user_mail(self):
        return

    def send_partner_mail(self):
        return

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        super()._onchange_partner_id()
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
