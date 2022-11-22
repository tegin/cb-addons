# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    inter_company_pos_session_id = fields.Many2one(
        "pos.session",
        check_company=False,
    )

    @api.depends("pos_order_ids.session_id.state")
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
