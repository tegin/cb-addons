# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_control_contact_partner_id = fields.Many2one("res.partner")
    credit_control_communication_ids = fields.One2many(
        "credit.control.communication",
        inverse_name="partner_id",
    )
    credit_control_communication_count = fields.Integer(
        compute="_compute_credit_control_communication_count"
    )

    @api.depends("credit_control_communication_ids")
    def _compute_credit_control_communication_count(self):
        for record in self:
            record.credit_control_communication_count = len(
                record.credit_control_communication_ids
            )
