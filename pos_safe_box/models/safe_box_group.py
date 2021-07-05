# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, exceptions, fields, models


class SafeBoxGroup(models.Model):
    _inherit = "safe.box.group"

    coin_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('id', 'in', safe_box_ids)]",
        string="Safe box where coins are stored on closure",
    )
    approve_coin_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('id', 'in', safe_box_ids)]",
        string="Safe box where coins are stored on approval",
    )
    note_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('id', 'in', safe_box_ids)]",
        string="Safe box where notes are stored on closure",
    )
    approve_note_safe_box_id = fields.Many2one(
        "safe.box",
        domain="[('id', 'in', safe_box_ids)]",
        string="Safe box where notes are stored on approval",
    )

    def session_validation_vals(self):
        return {
            "safe_box_group_id": self.id,
            "state": "draft",
            "line_ids": [
                (0, 0, {"safe_box_coin_id": coin.id}) for coin in self.coin_ids
            ],
        }

    def get_current_session_validation(self):
        self.ensure_one()
        validation = self.env["pos.session.validation"].search(
            [("safe_box_group_id", "=", self.id), ("state", "=", "draft")]
        )
        if not validation:
            return self.env["pos.session.validation"].create(
                self.session_validation_vals()
            )
        if len(validation.ids) > 1:
            raise exceptions.Warning(
                _("Only one validation session is allowed")
            )
        return validation
