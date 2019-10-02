# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    receiver_id = fields.Many2one(
        comodel_name="res.users",
        string="Receiver",
        track_visibility="onchange",
    )

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        self.receiver_id = self.env.user.id
        return res
