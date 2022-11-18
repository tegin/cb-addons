import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        res = super()._make_po_get_domain(company_id, values, partner)
        if values["supplier"].third_party_partner_id:
            res += (
                ("third_party_order", "=", True),
                (
                    "third_party_partner_id",
                    "=",
                    values["supplier"].third_party_partner_id.id,
                ),
            )
        else:
            res += (("third_party_order", "=", False),)
        return res

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        supplier = values["supplier"]
        if supplier.third_party_partner_id:
            res.update(
                {
                    "third_party_order": True,
                    "third_party_partner_id": supplier.third_party_partner_id.id,
                }
            )
        return res
