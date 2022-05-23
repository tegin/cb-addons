# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestMgmtsystemIndicatorsReport(TransactionCase):
    def setUp(self):
        super(TestMgmtsystemIndicatorsReport, self).setUp()
        self.uom = self.env.ref("uom.product_uom_cm")
        self.concept_1 = self.env["mgmtsystem.indicator.concept"].create(
            {
                "name": "Concept 1",
                "value_type": "float",
                "uom_id": self.uom.id,
                "reference_range_low": 2,
                "reference_range_high": 10,
            }
        )
        items = [
            {
                "name": "Line 1",
                "reference_range_low": 2,
                "reference_range_high": 10,
                "uom_id": self.uom.id,
                "value_type": "float",
            },
            {
                "name": "Line 2",
                "reference_range_low": 2,
                "reference_range_high": 10,
                "uom_id": self.uom.id,
                "value_type": "int",
            },
            {"name": "Line 3", "value_type": "bool"},
            {"name": "Line 4", "value_type": "str"},
            {"name": "Line 5", "concept_id": self.concept_1.id},
        ]
        self.template_1 = self.env[
            "mgmtsystem.indicators.report.template"
        ].create(
            {
                "name": "Template 1",
                "indicator_ids": [(0, 0, item) for item in items],
            }
        )

    def test_report_generation(self):
        report_generation = self.env["indicators.report.from.template"].create(
            {"template_id": self.template_1.id}
        )
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual("mgmtsystem.indicators.report", report._name)
        self.assertEqual(self.template_1.name, report.name)
        self.assertEqual(
            len(self.template_1.indicator_ids), len(report.indicator_ids)
        )

    def test_report_form(self):
        template = self.env["mgmtsystem.indicators.report.template"].create(
            {"name": "Template"}
        )
        with Form(template) as form:
            with form.indicator_ids.new() as indicator:
                indicator.concept_id = self.concept_1
                self.assertTrue(indicator.name)
                self.assertEqual(indicator.name, self.concept_1.name)

    def test_conforming_action(self):
        report_generation = self.env["indicators.report.from.template"].create(
            {"template_id": self.template_1.id}
        )
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertFalse(report.non_conformity_ids)
        report.conforming_action()
        self.assertEqual(report.state, "conforming")
        self.assertTrue(report.date)
        self.assertFalse(report.non_conformity_ids)

    def test_non_conforming_action(self):
        report_generation = self.env["indicators.report.from.template"].create(
            {"template_id": self.template_1.id}
        )
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertFalse(report.non_conformity_ids)
        nonconformity_action = report.non_conforming_action()
        with Form(
            self.env[nonconformity_action["res_model"]].with_context(
                **nonconformity_action["context"]
            )
        ) as form:
            form.partner_id = self.env.user.partner_id
        nonconformity = self.env[nonconformity_action["res_model"]].browse(
            form.id
        )
        self.assertEqual(report.state, "non_conforming")
        self.assertTrue(report.date)
        self.assertEqual(report.non_conformity_ids, nonconformity)

    def test_compute_interpretation_float(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {
                "name": "Indicator test",
                "reference_range_low": 2.5,
                "reference_range_high": 10.3,
            }
        )
        indicator.value_float = 5.3
        self.assertEqual(indicator.interpretation, "valid")
        indicator.value_float = 1.5
        self.assertEqual(indicator.interpretation, "invalid")
        indicator.value_float = 11.2
        self.assertEqual(indicator.interpretation, "invalid")

    def test_compute_interpretation_int(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {
                "name": "Indicator",
                "reference_range_low": 2,
                "reference_range_high": 10,
            }
        )
        indicator.value_int = 5
        self.assertEqual(indicator.interpretation, "valid")
        indicator.value_int = 1
        self.assertEqual(indicator.interpretation, "invalid")
        indicator.value_int = 11
        self.assertEqual(indicator.interpretation, "invalid")

    def test_compute_interpretation_bool(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {"name": "Indicator"}
        )
        indicator.value_bool = True
        self.assertFalse(indicator.interpretation)

    def test_compute_reference_range_with_range(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {
                "name": "Indicator",
                "reference_range_low": 2.5,
                "reference_range_high": 10.3,
                "uom_id": self.uom.id,
            }
        )
        indicator._compute_reference_range()
        self.assertEqual(
            indicator.reference_range_limit,
            "%.2f - %.2f"
            % (
                indicator.reference_range_low,
                indicator.reference_range_high,
            ),
        )

    def test_compute_reference_range_without_range(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {"name": "Indicator"}
        )
        indicator._compute_reference_range()
        self.assertFalse(indicator.reference_range_limit)

    def test_compute_reference_range_only_high_reference_limit(self):
        indicator = self.env["mgmtsystem.indicator"].create(
            {
                "name": "Indicator",
                "reference_range_high": 10.3,
                "uom_id": self.uom.id,
            }
        )
        indicator._compute_reference_range()
        self.assertEqual(
            indicator.reference_range_limit,
            " ≤ {:.2f}".format(indicator.reference_range_high),
        )
