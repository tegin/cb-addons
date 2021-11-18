# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    send_invoice_by_mail = fields.Boolean()
    email_integration = fields.Char()
    invoice_report_email_id = fields.Many2one(
        "ir.actions.report", domain=[("model", "=", "account.move")]
    )
    invoice_mail_exchange_type_id = fields.Many2one("edi.exchange.type")
