# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockRequestOrderTemplate(models.TransientModel):

    _name = "stock.request.order.template"

    template_id = fields.Many2one("stock.request.template", required=True)
    order_id = fields.Many2one("stock.request.order", required=True)
    company_id = fields.Many2one(
        "res.company", readonly=True, related="order_id.company_id"
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse", readonly=True, related="order_id.warehouse_id"
    )
    location_id = fields.Many2one(
        "stock.location", readonly=True, related="order_id.location_id"
    )

    @api.multi
    def doit(self):
        self.ensure_one()
        return self.order_id._apply_template(self.template_id)
