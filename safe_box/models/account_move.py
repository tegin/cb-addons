# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    safe_box_move_id = fields.Many2one(
        comodel_name="safe.box.move",
        readonly=True,
        string="Move",
        copy=False,
        delete="restrict",
    )
    safe_box_group_id = fields.Many2one(
        comodel_name="safe.box.group",
        related="safe_box_move_id.safe_box_group_id",
        store=True,
        readonly=True,
    )

    @api.multi
    def _post_validate(self):
        for move in self:
            safe_box_group = move.safe_box_move_id.safe_box_group_id
            if move.line_ids.filtered(
                lambda r: r.account_id.safe_box_group_id
                and r.account_id.safe_box_group_id != safe_box_group
            ):
                raise ValidationError(
                    _(
                        "Accounts with a related safe box must be under safe box "
                        "moves"
                    )
                )
        super(AccountMove, self)._post_validate()
