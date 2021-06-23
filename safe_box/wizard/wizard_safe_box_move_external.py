# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class WizardSafeBoxMoveExternal(models.TransientModel):
    _name = "wizard.safe.box.move.external"
    _description = "wizard.safe.box.move.external"

    safe_box_group_id = fields.Many2one("safe.box.group", required=True)
    safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('safe_box_group_id', '=', safe_box_group_id)]",
        required=True,
    )
    journal_id = fields.Many2one("account.journal", required=True)
    partner_id = fields.Many2one("res.partner")
    company_id = fields.Many2one(
        "res.company", related="journal_id.company_id", readonly=True
    )
    account_ids = fields.One2many(
        "account.account",
        related="safe_box_group_id.account_ids",
        readonly=True,
    )
    account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('id', 'not in', account_ids),"
        " ('company_id', '=', company_id)]",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="safe_box_group_id.currency_id",
        readonly=True,
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)

    def create_move_vals(self):
        return {"safe_box_group_id": self.safe_box_group_id.id}

    def create_account_move_vals(self, move, lines):
        return {
            "safe_box_move_id": move.id,
            "journal_id": self.journal_id.id,
            "line_ids": [(0, 0, line) for line in lines],
        }

    def create_safe_box_move_line_vals(self, move):
        return {
            "safe_box_move_id": move.id,
            "safe_box_id": self.safe_box_id.id,
            "amount": self.amount,
        }

    def create_account_line_vals(self, is_safe_box):
        if is_safe_box:
            account = self.safe_box_group_id.account_ids.filtered(
                lambda r: r.company_id.id == self.account_id.company_id.id
            )
            amount = self.amount
        else:
            account = self.account_id
            amount = -self.amount
        vals = {
            "account_id": account.id,
            "debit": amount > 0 and amount or 0,
            "credit": amount < 0 and -amount or 0,
        }
        if not is_safe_box and self.partner_id:
            vals["partner_id"] = self.partner_id.id
        return vals

    def run(self):
        self.ensure_one()
        move = self.env["safe.box.move"].create(self.create_move_vals())
        self.env["safe.box.move.line"].create(
            self.create_safe_box_move_line_vals(move)
        )
        lines = list()
        lines.append(self.create_account_line_vals(True))
        lines.append(self.create_account_line_vals(False))
        account_move = self.env["account.move"].create(
            self.create_account_move_vals(move, lines)
        )
        account_move.post()
        move.close()
        action = self.env.ref("safe_box.safe_box_move_action")
        result = action.read()[0]
        result["res_id"] = move.id
        result["views"] = [(False, "form")]
        return result
