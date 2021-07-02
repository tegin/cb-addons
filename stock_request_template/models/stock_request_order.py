# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    def _apply_template(self, template):
        for line in template.template_line_ids:
            vals = self._template_line_vals(template, line)
            self.env["stock.request"].create(vals)
        return {}

    def _template_line_vals(self, template, line):
        return {
            "warehouse_id": template.warehouse_id.id,
            "location_id": template.location_id.id,
            "company_id": template.company_id.id,
            "picking_policy": self.picking_policy,
            "expected_date": self.expected_date,
            "requested_by": self.requested_by.id,
            "procurement_group_id": self.procurement_group_id.id,
            "product_id": line.product_id.id,
            "product_uom_qty": line.product_uom_qty,
            "product_uom_id": line.product_uom_id.id,
            "order_id": self.id,
        }
