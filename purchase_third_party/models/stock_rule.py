from odoo import _, api, models
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.multi
    def _run_buy(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        values,
    ):
        if self.env.context.get("use_old_buy_rule", False):
            return super()._run_buy(
                product_id,
                product_qty,
                product_uom,
                location_id,
                name,
                origin,
                values,
            )
        cache = {}
        suppliers = product_id.seller_ids.filtered(
            lambda r: (
                not r.company_id or r.company_id == values["company_id"]
            )
            and (not r.product_id or r.product_id == product_id)
        )
        if not suppliers:
            msg = (
                _(
                    "There is no vendor associated to the product %s. "
                    "Please define a vendor for this product."
                )
                % product_id.display_name
            )
            raise UserError(msg)
        supplier = self._make_po_select_supplier(values, suppliers)
        partner = supplier.name
        # we put `supplier_info` in values for extensibility purposes
        values["supplier"] = supplier

        domain = self._make_po_get_domain(values, partner)
        if domain in cache:
            po = cache[domain]
        else:
            po = (
                self.env["purchase.order"]
                .sudo()
                .search([dom for dom in domain])
            )
            po = po[0] if po else False
            cache[domain] = po
        if not po:
            vals = self._prepare_purchase_order_supplier(
                product_id, product_qty, product_uom, origin, values, supplier
            )
            company_id = (
                values.get("company_id")
                and values["company_id"].id
                or self.env.user.company_id.id
            )
            po = (
                self.env["purchase.order"]
                .with_context(force_company=company_id)
                .sudo()
                .create(vals)
            )
            cache[domain] = po
        elif not po.origin or origin not in po.origin.split(", "):
            if po.origin:
                if origin:
                    po.write({"origin": po.origin + ", " + origin})
                else:
                    po.write({"origin": po.origin})
            else:
                po.write({"origin": origin})
        # Create Line
        po_line = False
        for line in po.order_line.filtered(
            lambda r: (
                r.product_id == product_id
                and r.product_uom == product_id.uom_po_id
            )
        ):
            if line._merge_in_existing_line(
                product_id,
                product_qty,
                product_uom,
                location_id,
                name,
                origin,
                values,
            ):
                vals = self._update_purchase_order_line_supplier(
                    product_id,
                    product_qty,
                    product_uom,
                    values,
                    line,
                    supplier,
                )
                po_line = line.write(vals)
                break
        if not po_line:
            vals = self._prepare_purchase_order_line(
                product_id, product_qty, product_uom, values, po, supplier
            )
            self.env["purchase.order.line"].sudo().create(vals)

    def _make_po_get_domain_supplier(self, values, supplier):
        res = self._make_po_get_domain(values, supplier.name)
        if supplier.third_party_partner_id:
            res += (
                ("third_party_order", "=", True),
                (
                    "third_party_partner_id",
                    "=",
                    supplier.third_party_partner_id.id,
                ),
            )
        return res

    @api.multi
    def _prepare_purchase_order_supplier(
        self, product_id, product_qty, product_uom, origin, values, supplier
    ):
        res = self._prepare_purchase_order(
            product_id, product_qty, product_uom, origin, values, supplier.name
        )
        if supplier.third_party_partner_id:
            res.update(
                {
                    "third_party_order": True,
                    "third_party_partner_id": supplier.third_party_partner_id.id,
                }
            )
        return res

    def _update_purchase_order_line_supplier(
        self, product_id, product_qty, product_uom, values, line, supplier
    ):
        return self._update_purchase_order_line(
            product_id, product_qty, product_uom, values, line, supplier.name
        )

    @api.multi
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, supplier
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier.name
        )
        procurement_uom_po_qty = res["product_qty"]
        seller = product_id._select_seller(
            partner_id=supplier.name,
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
