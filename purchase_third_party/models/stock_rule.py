from odoo import _, models
from odoo.exceptions import UserError


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

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        procurement_uom_po_qty = res["product_qty"]
        partner = values["supplier"].name
        seller = product_id._select_seller(
            partner_id=partner,
            quantity=procurement_uom_po_qty,
            date=po.date_order.date(),
            uom_id=product_id.uom_po_id,
        )
        if not seller.third_party_partner_id and not po.third_party_order:
            return res
        if seller.third_party_partner_id and not po.third_party_order:
            return UserError(
                _("The partner of the third party must be the same")
            )
        if seller.third_party_partner_id != po.third_party_partner_id:
            return UserError(
                _("The partner of the third party must be the same")
            )
        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(
                lambda x: x.company_id.id == values["company_id"].id
            )
        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.third_party_price,
                product_id.supplier_taxes_id,
                taxes_id,
                values["company_id"],
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and po.currency_id
            and seller.currency_id != po.currency_id
        ):
            price_unit = seller.currency_id.compute(price_unit, po.currency_id)
        res["third_party_price_unit"] = price_unit
        return res
