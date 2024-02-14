# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemIndicatorConcept(models.Model):

    _name = "mgmtsystem.indicator.concept"
    _description = "Mgmtsystem Indicator Concept"

    name = fields.Char()
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
    uom_id = fields.Many2one("uom.uom", string="Unit of measure")
    reference_range_low = fields.Float()
    reference_range_high = fields.Float()
    reference_interpretation = fields.Char()
    bool_expected = fields.Boolean(
        string="Expected value", help="Expected value for booleans"
    )

    _sql_constraints = [
        ("name_uniq", "UNIQUE (name)", "Concept name must be unique!"),
        (
            "check_reference_range",
            "CHECK(reference_range_low <= reference_range_high)",
            "Reference range low cannot be larger that reference range high",
        ),
    ]
