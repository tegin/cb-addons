# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestNumberOfHolidaysReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.holiday_type = self.env["hr.holidays.status"].create(
            {"name": "Holiday Type", "limit": True}
        )
        self.partner_id = self.env["res.partner"].create(
            {"name": "Pieter", "is_practitioner": True}
        )
        self.department = self.env["hr.department"].create(
            {"name": "Department"}
        )
        self.category = self.env["hr.employee.category"].create(
            {"name": "Tag 1"}
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Pieter",
                "partner_id": self.partner_id.id,
                "is_practitioner": True,
                "department_id": self.department.id,
                "category_ids": [(4, self.category.id)],
            }
        )
        self.holiday = self.env["hr.holidays"].create(
            {
                "name": "Test",
                "type": "remove",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "date_from": "2019-08-05 00:00:00",
                "date_to": "2019-08-09 23:59:59",
                "number_of_days_temp": 5,
            }
        )
        self.holiday.action_validate()
        self.wizard = self.env["wizard.holidays.count"].create(
            {
                "date_from": "2019-08-04",
                "date_to": "2019-08-10",
                "department_id": self.department.id,
                "category_ids": [(4, self.category.id)],
            }
        )

    def test_number_of_holidays_report(self):
        self.wizard.populate()
        self.assertIn(self.employee.id, self.wizard.employee_ids.ids)
        with self.assertRaises(UserError):
            self.env[
                "report.cb_number_of_holidays_report.report_holidays_count"
            ].get_report_values(False, {})

        data = dict({"form": {}})
        data["ids"] = self.wizard.ids
        data["model"] = self.wizard._name
        data["form"]["employee_ids"] = [self.employee.id]

        data["form"]["date_from"] = "2019-08-04"
        data["form"]["date_to"] = "2019-08-10"
        result = self.env[
            "report.cb_number_of_holidays_report.report_holidays_count"
        ].get_report_values(False, data)
        self.assertEqual(result["docs"][0]["num_of_days"], 5.0)
        self.assertEqual(result["docs"][0]["employee"], "Pieter")

        data["form"]["date_from"] = "2019-08-07"
        result = self.env[
            "report.cb_number_of_holidays_report.report_holidays_count"
        ].get_report_values(False, data)

        self.assertEqual(result["docs"][0]["num_of_days"], 3.0)

        data["form"]["date_to"] = "2019-08-08"
        result = self.env[
            "report.cb_number_of_holidays_report.report_holidays_count"
        ].get_report_values(False, data)

        self.assertEqual(result["docs"][0]["num_of_days"], 2.0)

        data["form"]["date_from"] = "2019-08-04"
        result = self.env[
            "report.cb_number_of_holidays_report.report_holidays_count"
        ].get_report_values(False, data)

        self.assertEqual(result["docs"][0]["num_of_days"], 4.0)

        printing = self.wizard.print_report()
        self.assertEqual(
            printing["report_name"],
            "cb_number_of_holidays_report.report_holidays_count",
        )
        self.assertEqual(
            printing["data"]["form"]["employee_ids"], [self.employee.id]
        )
