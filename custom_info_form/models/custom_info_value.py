# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class CustomInfoValue(models.Model):

    _inherit = "custom.info.value"

    @api.onchange("property_id")
    def _onchange_property_set_default_value(self):
        super()._onchange_property_set_default_value()
        for record in self:
            prop = record.property_id
            if prop.model != "custom.info.form":
                continue
            if not record.value and prop.compute_form_value:
                record["value_%s" % prop.field_type] = safe_eval(
                    record.property_id.compute_form_value,
                    record._get_safe_eval_data(),
                )

    def _get_safe_eval_data(self):
        return {
            "user": self.env.user,
        }

    def _selection_owner_id(self):
        result = super(CustomInfoValue, self)._selection_owner_id()
        model = self.env.ref("custom_info_form.model_custom_info_form")
        if all(m[0] != model.model for m in result):
            result.append((model.model, model.name))
        return result
