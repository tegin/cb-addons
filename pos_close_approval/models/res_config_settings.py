# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    pos_requires_approval = fields.Boolean(
        related="pos_config_id.requires_approval",
        string="Requires Approval",
        readonly=False,
    )
