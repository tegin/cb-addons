# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CustomInfoForm(models.Model):

    _name = "custom.info.form"
    _description = "Custom Info Form"

    _inherit = ["custom.info", "mail.thread"]

    name = fields.Char(compute="_compute_name", store=True,)
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        track_visibility="onchange",
        default=lambda r: r.env.user.partner_id,
    )
    custom_info_template_id = fields.Many2one(
        context={"default_model": _name}, required=True, readonly=True,
    )
    custom_info_ids = fields.One2many(context={"default_model": _name})

    @api.depends("partner_id", "custom_info_template_id")
    def _compute_name(self):
        for record in self:
            record.name = "{} - {}".format(
                record.partner_id.name, record.custom_info_template_id.name,
            )

    def _generate_form(self, template_id):
        domain = [
            ("partner_id", "=", self.env.user.partner_id.id),
            ("custom_info_template_id", "=", template_id),
        ]
        form = self.search(domain)
        if not form:
            form = self.create({"custom_info_template_id": template_id})
            form._onchange_custom_info_template_id()
        action = self.env.ref(
            "custom_info_form.custom_info_form_act_window_fullscreen"
        ).read()[0]
        action["res_id"] = form.id
        return action
