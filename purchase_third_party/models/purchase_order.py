from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    third_party_order = fields.Boolean(
        default=False, states=Purchase.READONLY_STATES
    )
    third_party_partner_id = fields.Many2one(
        "res.partner", states=Purchase.READONLY_STATES
    )

    tp_amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_all_tp",
        track_visibility="always",
    )
    tp_amount_tax = fields.Monetary(
        string="Taxes",
        store=True,
        readonly=True,
        compute="_compute_amount_all_tp",
    )
    tp_amount_total = fields.Monetary(
        string="Total",
        store=True,
        readonly=True,
        compute="_compute_amount_all_tp",
    )

    @api.depends("order_line.third_party_price_total")
    def _compute_amount_all_tp(self):
        for order in self:
            tp_amount_untaxed = tp_amount_tax = 0.0
            for line in order.order_line:
                tp_amount_untaxed += line.third_party_price_subtotal
                tp_amount_tax += line.third_party_price_tax
            order.update(
                {
                    "tp_amount_untaxed": order.currency_id.round(
                        tp_amount_untaxed
                    ),
                    "tp_amount_tax": order.currency_id.round(tp_amount_tax),
                    "tp_amount_total": tp_amount_untaxed + tp_amount_tax,
                }
            )

    @api.multi
    def action_rfq_send(self):
        res = super().action_rfq_send()
        if self.env.context.get("third_party_send"):
            ctx = res.get("context")
            ir_model_data = self.env["ir.model.data"]
            try:
                if self.env.context.get("send_rfq", False):
                    template_id = ir_model_data.get_object_reference(
                        "purchase_third_party", "email_template_edi_purchase"
                    )[1]
                else:
                    template_id = ir_model_data.get_object_reference(
                        "purchase_third_party",
                        "email_template_edi_purchase_done",
                    )[1]
            except ValueError:
                template_id = False
            ctx.update(
                {
                    "default_use_template": bool(template_id),
                    "default_template_id": template_id,
                    "tpl_partners_only": False,
                    "custom_layout": "purchase_third_party."
                    "mail_template_data_notification_email_purchase_order",
                    "not_display_company": True,
                }
            )
            res.update({"context": ctx})
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    third_party_price_unit = fields.Float(
        digits=dp.get_precision("Product Price")
    )

    third_party_price_subtotal = fields.Monetary(
        compute="_compute_amount_third_party", string="Subtotal", store=True
    )
    third_party_price_total = fields.Monetary(
        compute="_compute_amount_third_party", string="Total", store=True
    )
    third_party_price_tax = fields.Float(
        compute="_compute_amount_third_party", string="Tax", store=True
    )

    @api.depends("product_qty", "third_party_price_unit", "taxes_id")
    def _compute_amount_third_party(self):
        for line in self:
            taxes = line.taxes_id.compute_all(
                line.third_party_price_unit,
                line.order_id.currency_id,
                line.product_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update(
                {
                    "third_party_price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "third_party_price_total": taxes["total_included"],
                    "third_party_price_subtotal": taxes["total_excluded"],
                }
            )

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        res = super()._onchange_quantity()
        if not self.product_id:
            return res
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom,
        )
        if not seller or not self.order_id.third_party_order:
            self.third_party_price_unit = 0
            return res
        partner = self.order_id.third_party_partner_id
        if partner != seller.third_party_partner_id:
            raise ValidationError(_("Third party partner must be the same"))
        self.third_party_price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.third_party_price,
                self.product_id.supplier_taxes_id,
                self.taxes_id,
                self.company_id,
            )
            if seller
            else 0.0
        )
        return res
