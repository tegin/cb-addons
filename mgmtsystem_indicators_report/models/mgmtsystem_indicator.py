# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemIndicator(models.Model):

    _name = "mgmtsystem.indicator"
    _inherit = "mgmtsystem.indicator.abstract"
    _description = "Mgmtsystem Indicator"

    indicator_report_id = fields.Many2one(
        "mgmtsystem.indicators.report",
        ondelete="cascade",
        auto_join=True,
    )
    concept_id = fields.Many2one(store=True)

    value = fields.Char()

    value_representation = fields.Char(
        compute="_compute_value_representation", store=True
    )
    value_float = fields.Float()
    value_str = fields.Char()
    value_selection = fields.Char()
    value_int = fields.Integer()
    value_bool = fields.Boolean()
    bool_expected = fields.Boolean()
    reference_interpretation = fields.Char(
        related="concept_id.reference_interpretation"
    )
    reference_range_limit = fields.Char(
        string="Reference Range",
        compute="_compute_reference_range",
        store=True,
    )

    interpretation = fields.Selection(
        [("valid", "Valid"), ("invalid", "Invalid")],
        compute="_compute_interpretation",
        store=True,
    )

    def _get_reference_format(self):
        return self.uom_id.reference_format

    def _get_lang(self):
        return self.env.context.get("lang") or "en_US"

    @api.model
    def _get_reference_range_fields(self):
        return [
            "reference_range_low",
            "reference_range_high",
            "reference_interpretation",
        ]

    def _get_reference_range_values(self):
        return self.reference_range_low, self.reference_range_high

    def _get_reference_range_limit(self, low, high, reference_format, lang):
        range_limit = ""
        if reference_format and (high and low):
            range_limit = "{} - {}".format(
                lang.format(
                    reference_format,
                    low or 0,
                    grouping=True,
                ),
                lang.format(
                    reference_format,
                    high or 0,
                    grouping=True,
                ),
            )
        elif reference_format and high and not low:
            range_limit = " ≤ {}".format(
                lang.format(
                    reference_format,
                    high or 0,
                    grouping=True,
                ),
            )
        return range_limit

    @api.depends(_get_reference_range_fields)
    def _compute_reference_range(self):
        for rec in self:
            if rec.reference_interpretation:
                rec.reference_range_limit = rec.reference_interpretation
                continue
            reference_format = rec._get_reference_format()
            lang_code = rec._get_lang()
            lang = self.env["res.lang"]._lang_get(lang_code)
            low, high = rec._get_reference_range_values()
            range_limit = self._get_reference_range_limit(
                low, high, reference_format, lang
            )
            rec.reference_range_limit = range_limit

    @api.depends(
        "value_float",
        "value_int",
        "value_bool",
        "reference_range_low",
        "reference_range_high",
        "bool_expected",
    )
    def _compute_interpretation(self):
        for rec in self:
            label = False
            if rec.value_type == "bool":
                label = (
                    "valid"
                    if (bool(rec.value_bool) == bool(rec.bool_expected))
                    else "invalid"
                )
            if rec.reference_range_high or rec.reference_range_low:
                if rec.value_float:
                    if (
                        rec.value_float > rec.reference_range_high
                        or rec.value_float < rec.reference_range_low
                    ):
                        label = "invalid"
                    else:
                        label = "valid"

                elif rec.value_int:

                    if (
                        rec.value_int > rec.reference_range_high
                        or rec.value_int < rec.reference_range_low
                    ):
                        label = "invalid"
                    else:
                        label = "valid"
            rec.interpretation = label

    @api.depends(
        "value_float",
        "value_int",
        "value_selection",
        "value_str",
        "value_bool",
        "value",
    )
    def _compute_value_representation(self):
        for rec in self:
            if rec.value_type and hasattr(rec, "value_%s" % rec.value_type):
                value = getattr(rec, "value_%s" % rec.value_type)
                rec.value_representation = value
            else:
                rec.value_representation = rec.value
