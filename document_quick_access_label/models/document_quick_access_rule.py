# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DocumentQuickAccessRule(models.Model):
    _inherit = "document.quick.access.rule"

    label_id = fields.Many2one("printing.label.zpl2", "ZPL2 Label")
    icon = fields.Char()
    label_name = fields.Char()
    label_attrs = fields.Char()

    def _get_button_attrs(self):
        self.ensure_one()
        return self.label_attrs or "{}"
