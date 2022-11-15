# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = "product.template"

    def action_check_packaging(self):
        self.ensure_one()
        return self.product_variant_ids.action_check_packaging()


class ProductProduct(models.Model):

    _inherit = "product.product"

    def read_package_gs1_action(self, barcode):
        try:
            package = self.process_gs1_package_barcode(barcode)
        except Exception:
            result = self.action_check_packaging()
            result["context"].update(
                {
                    "default_status": _("Something went wrong. Please, try again."),
                    "default_state": "warning",
                }
            )
            return result
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

    def _barcode_gs1_package_domain(self, package_barcode):
        return [
            ("product_id", "=", self.id),
            ("barcode", "=", package_barcode),
        ]

    def process_gs1_package_barcode(self, barcode):
        barcode_decoded = self.env["gs1_barcode"].decode(barcode)
        package_barcode = barcode_decoded.get("01", False)
        if not package_barcode:
            package_barcode = barcode_decoded.get("02", False)
        if not package_barcode:
            raise ValidationError(_("Package cannot be found"))
        package = self.env["product.packaging"].search(
            self._barcode_gs1_package_domain(package_barcode)
        )
        if not package:
            package = self.env["product.packaging"].create(
                self._product_packaging_gs1_vals(package_barcode)
            )
        return package

    def _product_packaging_gs1_vals(self, package_barcode):
        return {
            "barcode": package_barcode,
            "qty": 1,
            "product_id": self.id,
            "name": package_barcode,
        }

    def action_check_packaging(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Search Package",
            "res_model": "barcode.action",
            "views": [[False, "form"]],
            "target": "new",
            "context": {
                "default_model": "product.product",
                "default_res_id": self.id,
                "default_method": "read_package_gs1_action",
                "default_status": _("Scan a GS1 package"),
            },
        }
