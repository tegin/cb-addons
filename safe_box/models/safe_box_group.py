# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class SafeBoxGroup(models.Model):
    """
    This entity joins the accounting information (account.account) with a
    set of safe boxes.
    The balance of the accounts must be equal to the balance of the safe boxes,
    however, the amount on each safe box can be shared between several companies
    """

    _name = "safe.box.group"
    _description = "Safe box group"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    account_ids = fields.One2many(
        comodel_name="account.account",
        inverse_name="safe_box_group_id",
        string="Accounts",
    )
    safe_box_ids = fields.One2many(
        comodel_name="safe.box",
        inverse_name="safe_box_group_id",
        string="Safe boxes",
    )
    coin_ids = fields.One2many(
        comodel_name="safe.box.coin",
        inverse_name="safe_box_group_id",
        string="Coins",
    )
    currency_id = fields.Many2one("res.currency", required=True)
    sequence_id = fields.Many2one("ir.sequence", string="Entry Sequence")

    @api.model
    def _create_sequence(self, vals):
        """Create new no_gap entry sequence for every new Safe Box Group"""
        seq = {
            "name": vals["name"],
            "implementation": "no_gap",
            "prefix": vals["code"],
            "padding": 4,
            "number_increment": 1,
            "use_date_range": True,
        }
        seq = self.env["ir.sequence"].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = 1
        return seq

    @api.model
    def create(self, vals):
        if not vals.get("sequence_id"):
            vals.update({"sequence_id": self.sudo()._create_sequence(vals).id})
        return super(SafeBoxGroup, self).create(vals)

    def recompute_amount(self):
        for record in self.sudo():
            record.safe_box_ids.recompute_amount()
            record.account_ids.recompute_amount()

    def action_count_money(self):
        self.ensure_one()
        action = self.env.ref("safe_box.wizard_safe_box_count_action").read()[
            0
        ]
        wizard = self.env["wizard.safe.box.count"].create(
            {"safe_box_group_id": self.id}
        )
        action["res_id"] = wizard.id
        return action
