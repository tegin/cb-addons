# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemIndicatorsReport(models.Model):

    _name = "mgmtsystem.indicators.report"
    _inherit = "mgmtsystem.indicator.report.abstract"
    _description = "Mgmtsystem Indicators Report"

    date = fields.Date()

    notes = fields.Text()

    external_identifier = fields.Char()

    validation_partner = fields.Many2one("res.partner")

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

    def conforming_action(self):
        for rec in self:
            rec.state = "conforming"
            if not rec.date:
                rec.date = fields.Date.today()

    def non_conforming_action(self):
        for rec in self:
            rec.state = "non_conforming"
            if not rec.date:
                rec.date = fields.Date.today()
