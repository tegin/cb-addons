# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    pos_safe_box_group_id = fields.Many2one(
        related="pos_config_id.safe_box_group_id",
        string="Safe box system",
        readonly=False,
    )
