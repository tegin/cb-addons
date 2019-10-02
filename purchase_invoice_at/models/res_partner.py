# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    to_invoice = fields.Boolean(
        string="Can invoice directly",
        help="Supplier may invoice directly to the partner",
    )
    invoiced_purchase_count = fields.Integer(
        compute="_compute_invoiced_purchases_count",
        string="# Invoiced Purchases",
    )
    invoiced_purchase_ids = fields.One2many(
        "purchase.order",
        string="Invoiced Purchases",
        inverse_name="partner_to_invoice_id",
        readonly=True,
    )

    @api.depends("invoiced_purchase_ids")
    def _compute_invoiced_purchases_count(self):
        for record in self:
            record.invoiced_purchase_count = len(record.invoiced_purchase_ids)
