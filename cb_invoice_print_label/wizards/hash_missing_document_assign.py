# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HashMissingDocumentAssign(models.TransientModel):
    _inherit = "hash.missing.document.assign"

    @api.onchange("object_id")
    def _onchange_object_set_domain(self):
        res = super()._onchange_object_set_domain()
        if self.object_id and self.object_id._name == "account.invoice":
            res["domain"]["object_id"].append(
                ("type", "in", ["in_invoice", "in_refund"])
            )
