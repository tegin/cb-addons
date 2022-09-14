# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    third_party_sale_order_ids = fields.One2many(
        "sale.order",
        inverse_name="third_party_move_id",
        readonly=True,
        string="Third party related Sale Orders",
    )
    third_party_sale_order = fields.Boolean(
        compute="_compute_third_party_sale_order",
        store=True,
        readonly=True,
    )

    @api.depends("third_party_sale_order_ids")
    def _compute_third_party_sale_order(self):
        for record in self:
            record.third_party_sale_order = bool(
                record.third_party_sale_order_ids
            )
