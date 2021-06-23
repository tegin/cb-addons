# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.tools import float_compare


class WizardSafeBoxCount(models.TransientModel):
    _name = "wizard.safe.box.count"
    _description = "wizard.safe.box.count"

    safe_box_group_id = fields.Many2one("safe.box.group", required=True)
    safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('safe_box_group_id', '=', safe_box_group_id)]",
        required=False,
    )
    coin_ids = fields.One2many(
        "wizard.safe.box.count.coin",
        inverse_name="safe_box_count_id",
        domain="[('safe_box_coin_id', 'in', safe_box_coin_ids)]",
        string="Coins",
    )
    safe_box_coin_ids = fields.Many2many(
        "safe.box.coin", related="safe_box_id.coin_ids", readonly=True
    )
    state = fields.Selection(
        [("equal", "Equal"), ("different", "Different")], default=False
    )
    status = fields.Char()

    @api.onchange("safe_box_id")
    def _onchange_safe_box_id(self):
        self.coin_ids = self.env["wizard.safe.box.count.coin"].create(
            [
                {"safe_box_coin_id": coin.id, "safe_box_count_id": self.id}
                for coin in self.safe_box_id.coin_ids
            ]
        )

    @api.onchange("coin_ids")
    def validate(self):
        self.ensure_one()
        self.safe_box_id.recompute_amount()
        amount = sum(self.coin_ids.mapped("amount"))
        if (
            float_compare(amount, self.safe_box_id.amount, precision_digits=6)
            == 0
        ):
            self.state = "equal"
            self.status = _("Cash Box amount is correct")
        else:
            self.state = "different"
            self.status = _("Cash Box amount is different")


class WizardSafeBoxCountCoin(models.TransientModel):
    _name = "wizard.safe.box.count.coin"
    _description = "Count coins"

    safe_box_count_id = fields.Many2one("wizard.safe.box.count", readonly=True)
    safe_box_coin_id = fields.Many2one(
        "safe.box.coin", required=True, string="Coin"
    )
    value = fields.Integer(required=True, default=0)
    amount = fields.Float(compute="_compute_amount")

    @api.depends("value", "safe_box_coin_id")
    def _compute_amount(self):
        for record in self:
            record.amount = record.safe_box_coin_id.rate * record.value
