# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_post(self):
        lines_of_moves_to_reconcile = self.line_ids.filtered(
            lambda line: line.move_id.state != "posted"
            and line.third_party_sale_order_id
        )
        result = super(AccountBankStatement, self).button_post()
        for line in lines_of_moves_to_reconcile:
            sale_order = line.third_party_sale_order_id
            move_line = line.move_id.line_ids.filtered(
                lambda l: l.account_internal_type in ("receivable", "payable")
            )
            (sale_order.third_party_move_id.line_ids | move_line).filtered(
                lambda l: l.account_id in move_line.mapped("account_id")
            ).reconcile()
        return result
