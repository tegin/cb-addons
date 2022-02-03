# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemIndicatorReportAbstract(models.AbstractModel):

    _name = "mgmtsystem.indicator.report.abstract"
    _description = "Abstract Mgmtsystem Indicator Report"

    name = fields.Char()

    items_blocked = fields.Boolean(default=False)


class MgmtsystemIndicatorAbstract(models.AbstractModel):

    _name = "mgmtsystem.indicator.abstract"
    _description = "Abstract Mgmtsystem Indicator"

    concept_id = fields.Many2one(comodel_name="mgmtsystem.indicator.concept")
    name = fields.Char(required=True)

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

    item_blocked = fields.Boolean(default=False)

    _sql_constraints = [
        (
            "check_reference_range",
            "CHECK(concept_id is not null "
            "or reference_range_low <= reference_range_high)",
            "Reference range low cannot be larger that reference range high",
        ),
    ]
