# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class SafeBoxCoin(models.Model):
    """
    This entity contains the name and rate of the different coins and bills.
    Useful to recount all the amounts of a safe box
    """

    _name = "safe.box.coin"
    _description = "Safe box coin"
    _order = "rate ASC"

    name = fields.Char(required=True)
    rate = fields.Float(required=True)
    safe_box_group_id = fields.Many2one(
        comodel_name="safe.box.group", string="Safe box group"
    )
    safe_box_ids = fields.Many2many(
        comodel_name="safe.box",
        relation="safe_box_coin_rel",
        column1="coin_id",
        column2="safe_box_id",
        string="Safe boxes",
    )
