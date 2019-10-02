# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestCbHolidaysMinimumDays(TransactionCase):
    def setUp(self):
        super(TestCbHolidaysMinimumDays, self).setUp()
        self.employee = self.env["hr.employee"].create({"name": "Employee 1"})
        self.holiday_type = self.env["hr.holidays.status"].create(
            {"name": "Leave Type Test", "minimum_time": 7}
        )
        self.allocation = self.env["hr.holidays"].create(
            {
                "name": "Test",
                "type": "add",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "number_of_days_temp": 10,
            }
        )
        self.allocation.action_validate()

    def test_cb_holidays_minimum_days(self):
        holiday = self.env["hr.holidays"].create(
            {
                "name": "Test",
                "type": "remove",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "date_from": "2019-05-21",
                "date_to": "2019-05-22",
                "number_of_days_temp": 2,
            }
        )
        holiday.action_validate()
        self.assertEqual(
            holiday.warning_minimum,
            "Warning: The number of days is less than the"
            " minimum for that holiday type (7)",
        )

        holiday = self.env["hr.holidays"].new(
            {
                "name": "Test",
                "type": "remove",
                "employee_id": self.employee.id,
                "holiday_status_id": self.holiday_type.id,
                "date_from": "2019-07-10",
                "date_to": "2019-07-19",
                "number_of_days_temp": 7,
            }
        )
        self.assertEqual(
            holiday.warning_minimum,
            "Warning: The number of days remaining (1) will"
            " be less than the minimum for that holiday type (7)",
        )
