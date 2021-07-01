from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    third_party_partner_id = fields.Many2one("res.partner", check_company=True)
    third_party_price = fields.Float(digits="Product Price")

    @api.onchange("third_party_partner_id")
    def _onchange_third_party_partner(self):
        if not self.third_party_partner_id:
            self.third_party_price = False

    @api.constrains("third_party_partner_id", "third_party_price")
    def _check_third_party_price(self):
        for rec in self:
            if rec.third_party_partner_id and not rec.third_party_price:
                raise ValidationError(_("Third party price must be defined"))

    @api.constrains("third_party_partner_id", "name", "product_id")
    def _check_third_party(self):
        for rec in self.filtered(lambda r: r.third_party_partner_id):
            if rec.product_id and self.search(
                [
                    ("id", "!=", rec.id),
                    ("product_id", "=", rec.product_id.id),
                    ("name", "=", rec.name.id),
                    (
                        "third_party_partner_id",
                        "!=",
                        rec.third_party_partner_id.id,
                    ),
                ],
                limit=1,
            ):
                raise ValidationError(
                    _(
                        "The product cannot be defined with different third party "
                        "configuration."
                    )
                )
            elif self.search(
                [
                    ("id", "!=", rec.id),
                    ("product_tmpl_id", "=", rec.product_tmpl_id.id),
                    ("name", "=", rec.name.id),
                    (
                        "third_party_partner_id",
                        "!=",
                        rec.third_party_partner_id.id,
                    ),
                ],
                limit=1,
            ):
                raise ValidationError(
                    _(
                        "The product cannot be defined with different third party "
                        "configuration."
                    )
                )
