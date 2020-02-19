# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardSafeBoxMove(models.TransientModel):
    _name = "wizard.safe.box.move"
    _description = "wizard.safe.box.move"

    safe_box_group_id = fields.Many2one("safe.box.group", required=True)
    initial_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('safe_box_group_id', '=', safe_box_group_id)]",
        required=True,
    )
    end_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('safe_box_group_id', '=', safe_box_group_id)]",
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="safe_box_group_id.currency_id",
        readonly=True,
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)

    def create_move_vals(self):
        return {"safe_box_group_id": self.safe_box_group_id.id}

    def create_line_vals(self, move, initial=True):
        return {
            "safe_box_move_id": move.id,
            "safe_box_id": (initial and self.initial_safe_box_id.id)
            or self.end_safe_box_id.id,
            "amount": initial and -self.amount or self.amount,
        }

    @api.multi
    def run(self):
        self.ensure_one()
        move = self.env["safe.box.move"].create(self.create_move_vals())
        line_obj = self.env["safe.box.move.line"]
        line_obj.create(self.create_line_vals(move, True))
        line_obj.create(self.create_line_vals(move, False))
        move.close()
        action = self.env.ref("safe_box.safe_box_move_action")
        result = action.read()[0]
        result["res_id"] = move.id
        result["views"] = [(False, "form")]
        return result
