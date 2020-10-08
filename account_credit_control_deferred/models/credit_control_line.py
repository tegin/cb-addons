# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreditControlLine(models.Model):

    _inherit = "credit.control.line"

    channel = fields.Selection(
        selection_add=[("email_deferred", "Email Deferred")]
    )
    balance_due = fields.Float(
        string="Due balance",
    )
    original_balance_due = fields.Float(
        string="Original Due balance",
        required=True,
        readonly=True,
    )

    @api.model
    def _prepare_from_move_line(
        self,
        move_line,
        level,
        controlling_date,
        open_amount,
        default_lines_vals,
    ):
        data = super()._prepare_from_move_line(
            move_line, level, controlling_date, open_amount, default_lines_vals
        )
        data.update(
            {
                "original_balance_due": data["balance_due"],
            }
        )
        return data

    def _update_balance(self, user_currency):
        for record in self:
            ml_currency = record.move_line_id.currency_id
            if ml_currency and ml_currency != user_currency:
                open_amount = record.move_line_id.amount_residual_currency
            else:
                open_amount = record.move_line_id.amount_residual
            record.balance_due = open_amount
