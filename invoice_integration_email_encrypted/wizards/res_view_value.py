# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResViewValue(models.TransientModel):
    _name = "res.view.value"
    _inherit = "email.encryptor"

    @api.model
    def _default_value(self):
        ctx = self.env.context
        partner = self.env[ctx.get("default_model")].browse(
            ctx.get("default_res_id")
        )
        encrypted = getattr(partner, ctx.get("default_field"))
        return self._decrypt_value(encrypted)

    model = fields.Char()
    res_id = fields.Integer(required=True)
    value = fields.Char(readonly=True, default=_default_value)
    field = fields.Char(required=True)
