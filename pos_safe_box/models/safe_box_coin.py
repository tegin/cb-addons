# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SafeBoxCoin(models.Model):
    _inherit = "safe.box.coin"

    type = fields.Selection(
        [("coin", "Coin"), ("note", "Note")], default="coin", required=True
    )
