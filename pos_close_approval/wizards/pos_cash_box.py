# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class PosCashBox(models.TransientModel):

    _name = "pos.cash.box"
    _description = "Cash In/Out manually in pos session"

    session_id = fields.Many2one("pos.session", required=True)
    move_type = fields.Selection(
        [("in", "In"), ("out", "Out")], "Type", required=True, default="in"
    )
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(related="session_id.currency_id")
    reason = fields.Text()

    def run(self):
        self.ensure_one()
        translated_type = {
            "in": _("in"),
            "out": _("out"),
        }
        self.session_id.try_cash_in_out(
            self.move_type,
            self.amount,
            self.reason,
            {
                "translatedType": translated_type[self.move_type],
                "formattedAmount": self.currency_id.format(self.amount),
            },
        )
        return {"type": "ir.actions.act_window_close"}
