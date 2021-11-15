# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemIndicatorsReport(models.Model):

    _name = "mgmtsystem.indicators.report"
    _inherit = [
        "mgmtsystem.indicator.report.abstract",
        "mgmtsystem.nonconformity.abstract",
    ]
    _description = "Mgmtsystem Indicators Report"

    date = fields.Date()

    notes = fields.Text()

    external_identifier = fields.Char()

    validation_partner_id = fields.Many2one("res.partner")

    location = fields.Char()

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("conforming", "Conforming"),
            ("non_conforming", "Non conforming"),
        ],
        default="draft",
    )
    indicator_ids = fields.One2many(
        "mgmtsystem.indicator", inverse_name="indicator_report_id", copy=True
    )
    report_pdf = fields.Binary()

    def _get_non_conformity_description(self):
        description = (
            "The indicators report presented "
            "the following indicators values invalid:"
        )
        indicators = self.indicator_ids.filtered(
            lambda r: r.interpretation == "invalid"
        )
        for indicator in indicators:
            description = description + "\n {} with value {} {}".format(
                indicator.name,
                indicator.value_representation,
                indicator.uom_id.name,
            )
        return description

    def _get_non_conformity_vals(self):
        return {
            "default_name": self.name,
            "default_partner_id": self.validation_partner_id.id,
            "default_responsible_user_id": self.env.user.id,
            "default_manager_user_id": self.env.user.id,
            "default_description": self._get_non_conformity_description(),
            "default_res_id": self.id,
            "default_res_model": self._name,
        }

    def _create_non_conformity(self):
        action = self.env["mgmtsystem.nonconformity"].get_formview_action()
        action["context"] = self._get_non_conformity_vals()
        return action

    def conforming_action(self):
        for rec in self:
            rec.state = "conforming"
            if not rec.date:
                rec.date = fields.Date.today()

    def non_conforming_action(self):
        self.ensure_one()
        return self._create_non_conformity()


class MgmtsystemNonconformity(models.Model):
    _inherit = "mgmtsystem.nonconformity"

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for record in result:
            if (
                record.res_id
                and record.res_model
                and record.res_model == "mgmtsystem.indicators.report"
            ):
                report = self.env[record.res_model].browse(record.res_id)
                report.state = "non_conforming"
                if not report.date:
                    report.date = fields.Date.today()
        return result
