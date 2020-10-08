# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def action_view_product_supplierinfo(self):
        self.ensure_one()
        action = self.env.ref(
            "product.product_supplierinfo_type_action"
        ).read()[0]
        action["domain"] = [
            "|",
            ("name", "=", self.id),
            ("third_party_partner_id", "=", self.id),
        ]
        return action
