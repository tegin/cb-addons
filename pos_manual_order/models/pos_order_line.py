# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class PosOrderLine(models.Model):

    _inherit = "pos.order.line"

    @api.onchange("qty", "discount", "price_unit", "tax_ids")
    def _onchange_qty(self):
        if self.product_id:
            if not self.order_id.pricelist_id:
                raise UserError(
                    _("You have to select a pricelist in the sale form.")
                )
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            if self.tax_ids:
                taxes = self.tax_ids.compute_all(
                    price,
                    self.order_id.pricelist_id.currency_id,
                    self.qty,
                    product=self.product_id,
                    partner=False,
                )
                self.price_subtotal = taxes["total_excluded"]
                self.price_subtotal_incl = taxes["total_included"]
