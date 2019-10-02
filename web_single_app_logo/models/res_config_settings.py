# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    single_app_logo = fields.Binary(string="Shared logo")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        single_app_logo = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("app.logo", default=False)
        )
        res.update(single_app_logo=single_app_logo)
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "app.logo", self.single_app_logo
        )
        return res
