# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountAccount(models.Model):
    _inherit = "account.account"

    safe_box_group_id = fields.Many2one(
        comodel_name="safe.box.group",
        string="Safe box group",
        ondelete="restrict",
    )
    safe_box_currency_id = fields.Many2one(
        "res.currency", related="safe_box_group_id.currency_id", readonly=True
    )
    safe_box_amount = fields.Monetary(currency_field="safe_box_currency_id")

    def recompute_amount(self):
        """Updates the balance of the account"""
        for record in self:
            if record.safe_box_group_id:
                moves = self.env["account.move.line"].search(
                    [
                        ("account_id", "=", record.id),
                        ("move_id.state", "=", "posted"),
                    ]
                )
                record.safe_box_amount = sum(moves.mapped("balance")) or 0.0

    @api.constrains("safe_box_group_id")
    def _check_safe_box_group(self):
        """
        Checks that the safe_box_group is set properly:
            - Safe box can only be edited if the balance is 0
            - Only one account by company is allowed on a safe box group
        """
        for record in self:
            lines = self.env["account.move.line"].search(
                [
                    ("account_id", "=", record.id),
                    ("move_id.state", "=", "posted"),
                ]
            )
            if float_compare(sum(lines.mapped("balance")), 0, precision_digits=6) != 0:
                raise ValidationError(
                    _(
                        "Safe box group cannot be set if the account has "
                        "not zero value"
                    )
                )
            sb_group = record.safe_box_group_id
            if sb_group and len(sb_group.account_ids) != len(
                sb_group.mapped("account_ids.company_id")
            ):
                raise ValidationError(_("Only one account by company is allowed"))
