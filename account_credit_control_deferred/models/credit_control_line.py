# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CreditControlLine(models.Model):

    _inherit = "credit.control.line"

    channel = fields.Selection(
        selection_add=[("email_deferred", "Email Deferred")]
    )
