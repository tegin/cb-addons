# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CreditControlPolicyLevel(models.Model):

    _inherit = "credit.control.policy.level"

    channel = fields.Selection(selection_add=[("email_deferred", "Email Deferred")])
