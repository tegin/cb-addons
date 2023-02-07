# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MgmtsystemNonconformity(models.Model):

    _inherit = "mgmtsystem.nonconformity"

    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)

    def access_related_item(self):
        self.ensure_one()
        if not self.res_model or self.res_model not in self.env:
            return False
        records = self.env[self.res_model].browse(self.res_id).exists()
        if not records:
            return False
        return {
            "name": _("Related Record"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": records._name,
            "res_id": records.id,
        }
