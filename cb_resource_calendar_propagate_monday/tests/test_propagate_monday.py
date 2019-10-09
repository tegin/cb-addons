# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPropagateMonday(TransactionCase):
    def setUp(self):
        super().setUp()
        self.calendar_id = self.env["resource.calendar"].create(
            {"name": "Calendar"}
        )

    def test_clone_monday(self):
        self.assertEqual(len(self.calendar_id.attendance_ids), 10)
        self.assertEqual(self.calendar_id.attendance_ids[2].dayofweek, "1")
        self.assertEqual(self.calendar_id.attendance_ids[2].hour_from, 8.0)
        self.assertEqual(self.calendar_id.attendance_ids[2].hour_to, 12.0)

        self.calendar_id.attendance_ids[0].write(
            {"hour_from": 7, "hour_to": 11}
        )
        self.calendar_id.propagate_mondays()

        for i in range(0, 5):
            self.assertEqual(
                self.calendar_id.attendance_ids[i * 2].dayofweek, str(i)
            )
            self.assertEqual(
                self.calendar_id.attendance_ids[i * 2].hour_from, 7
            )
            self.assertEqual(
                self.calendar_id.attendance_ids[i * 2].hour_to, 11
            )
