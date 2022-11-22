# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    account_move = fields.Many2one(check_company=False)
