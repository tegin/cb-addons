# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountInvoiceIntegration(models.Model):
    _inherit = "account.invoice.integration"

    email_password = fields.Char()
