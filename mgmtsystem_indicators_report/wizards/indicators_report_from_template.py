# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IndicatorsReportFromTemplate(models.TransientModel):

    _name = "indicators.report.from.template"
    _description = (
        " This wizard allows to create "
        "an indicators report using a template"
    )
    test = fields.Char()
    template_id = fields.Many2one(
        "mgmtsystem.indicators.report.template", required=True
    )

    def generate(self):
        self.ensure_one()
        report = self.template_id._generate_report()
        return report.get_formview_action()
