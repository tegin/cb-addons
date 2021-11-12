# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemIndicatorsReportTemplate(models.Model):

    _name = "mgmtsystem.indicators.report.template"
    _inherit = "mgmtsystem.indicator.report.abstract"
    _description = "Mgmtsystem Indicators Report Template"

    indicator_ids = fields.One2many(
        "mgmtsystem.indicator.template", inverse_name="template_id"
    )

    def _generate_report_vals(self):
        return {
            "name": self.name,
            "indicator_ids": [
                (0, 0, item._generate_report_indicator_vals())
                for item in self.indicator_ids
            ],
        }

    def _generate_report(self):
        return self.env["mgmtsystem.indicators.report"].create(
            self._generate_report_vals()
        )


class MgmtsystemIndicatorTemplate(models.Model):

    _name = "mgmtsystem.indicator.template"
    _inherit = "mgmtsystem.indicator.abstract"
    _description = "Mgmtsystem Indicator Template"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "mgmtsystem.indicators.report.template", ondelete="cascade"
    )
    concept_id = fields.Many2one(comodel_name="mgmtsystem.indicator.concept")
    name = fields.Char()

    uom_id = fields.Many2one("uom.uom", string="Unit of measure")

    reference_range_low = fields.Float()
    reference_range_high = fields.Float()

    value_type = fields.Selection(
        [
            ("str", "String"),
            ("float", "Float"),
            ("bool", "Boolean"),
            ("int", "Integer"),
            ("selection", "Selection"),
        ]
    )
    selection_options = fields.Char(translate=True)

    sequence = fields.Integer(default=20)

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    _sql_constraints = [
        (
            "concept_id_uniq",
            "UNIQUE(concept_id, template_id)",
            "Indicator concept must be unique.",
        ),
    ]

    @api.onchange("concept_id")
    def _onchange_observation_concept(self):
        if self.concept_id:
            self.name = self.concept_id.name
            self.value_type = self.concept_id.value_type
            self.selection_options = self.concept_id.selection_options
            self.uom_id = self.concept_id.uom_id
            self.reference_range_low = self.concept_id.reference_range_low
            self.reference_range_high = self.concept_id.reference_range_high
        return {}

    def _generate_report_indicator_vals(self):
        concept = self.concept_id or self
        return {
            "uom_id": concept.uom_id.id,
            "concept_id": self.concept_id.id,
            "name": concept.name,
            "reference_range_high": concept.reference_range_high,
            "reference_range_low": concept.reference_range_low,
            "display_type": self.display_type,
            "sequence": self.sequence,
            "selection_options": concept.selection_options,
            "value_type": concept.value_type,
        }
