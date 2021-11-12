from odoo import fields, models, tools


class IndicatorsReport(models.Model):
    _name = "indicators.report"
    _description = "Indicators Report"
    _auto = False
    _rec_name = "date"
    _order = "date desc"

    name = fields.Char(readonly=True, string="Report Name")
    date = fields.Date(readonly=True)
    location = fields.Char()
    validation_partner = fields.Many2one("res.partner", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("conforming", "Conforming"),
            ("non_conforming", "Non conforming"),
        ],
        readonly=True,
    )

    indicator_report_id = fields.Many2one(
        "mgmtsystem.indicators.report", readonly=True
    )
    concept_id = fields.Many2one(
        comodel_name="mgmtsystem.indicator.concept", readonly=True
    )
    uom_id = fields.Many2one("uom.uom", readonly=True)
    value_representation = fields.Char(readonly=True)
    reference_range_limit = fields.Char(
        string="Reference Range", readonly=True
    )
    interpretation = fields.Selection(
        [("valid", "Valid"), ("invalid", "Invalid")], readonly=True
    )

    def _query(self, with_clause="", fields=None, groupby="", from_clause=""):
        if fields is None:
            fields = {}
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            min(i.id) as id,
            i.concept_id as concept_id,
            i.uom_id as uom_id,
            i.value_representation as value_representation,
            i.reference_range_limit as reference_range_limit,
            i.interpretation as interpretation,
            r.name as name,
            r.date as date,
            r.validation_partner as validation_partner,
            r.location as location,
            r.state as state,
            r.id as indicator_report_id
        """
        for field in fields.values():
            select_ += field

        from_ = (
            """
                mgmtsystem_indicator i
                    join mgmtsystem_indicators_report r on (i.indicator_report_id=r.id)
                %s
        """
            % from_clause
        )

        groupby_ = """
            i.concept_id,
            i.uom_id,
            i.value_representation,
            i.reference_range_limit,
            i.interpretation,
            r.name,
            r.date,
            r.validation_partner,
            r.location,
            r.state,
            r.id %s
        """ % (
            groupby
        )

        return (
            "%s (SELECT %s FROM %s WHERE i.concept_id IS NOT NULL GROUP BY %s)"
            % (with_, select_, from_, groupby_)
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # pylint: disable=E8103
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)"""
            % (self._table, self._query())
        )
