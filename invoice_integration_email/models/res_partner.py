# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    email_integration = fields.Char()
    invoice_report_email_id = fields.Many2one(
        "ir.actions.report", domain=[("model", "=", "account.invoice")]
    )
