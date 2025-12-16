# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAccessFast(models.Model):
    _name = "ir.access.fast"
    _description = "IR Access Fast Model"

    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', model_id)]",
        required=True,
        ondelete="cascade",
    )

    _sql_constraints = [
        ("name_unique", "unique(name)", "The name must be unique."),
    ]
