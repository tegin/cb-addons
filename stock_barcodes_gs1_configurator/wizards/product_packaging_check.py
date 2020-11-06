# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ProductPackagingCheck(models.TransientModel):
    _name = "product.packaging.check"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Wizard to check packaging"

    product_id = fields.Many2one("product.product")
    barcode = fields.Char()

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode
        package = self.process_barcode(barcode)
        result = self.env.ref("product.action_packaging_view").read()[0]
        result.update(
            {
                "views": [(False, "form")],
                "res_id": package.id,
                "target": "new",
                "view_mode": "form",
            }
        )
        return result

    def _barcode_domain(self, package_barcode):
        return [
            ("product_id", "=", self.product_id.id),
            ("barcode", "=", package_barcode),
        ]

    def process_barcode(self, barcode):
        try:
            barcode_decoded = self.env["gs1_barcode"].decode(barcode)
            package_barcode = barcode_decoded.get("01", False)
            if not package_barcode:
                raise ValidationError(_("Package cannot be found"))
            package = self.env["product.packaging"].search(
                self._barcode_domain(package_barcode)
            )
            if not package:
                package = self.env["product.packaging"].create(
                    self._product_packaging_vals(package_barcode)
                )
            return package
        except ValidationError:
            raise
        except Exception:
            raise ValidationError(_("Barcode cannot be decoded"))

    def _product_packaging_vals(self, package_barcode):
        return {
            "barcode": package_barcode,
            "qty": 1,
            "product_id": self.product_id.id,
            "name": package_barcode,
        }
