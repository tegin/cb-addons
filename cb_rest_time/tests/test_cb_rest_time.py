# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import datetime, time


class TestCbRestTime(TransactionCase):

    def setUp(self):
        super(TestCbRestTime, self).setUp()
        self.calendar = self.env['resource.calendar'].create({
            'name': 'Calendar 1',
            'attendance_ids': []
        })

        for i in range(0, 7):
            self.env['resource.calendar.attendance'].create({
                'name': 'Day ' + str(i),
                'dayofweek': str(i),
                'hour_from': 8.0,
                'hour_to': 17.0,
                'rest_time': 1.0,
                'calendar_id': self.calendar.id,
            })

        self.employee = self.env['hr.employee'].create({
            'name': 'Employee',
            'resource_calendar_id': self.calendar.id
        })

    def test_cb_rest_time(self):
        today = fields.Date.from_string(fields.Date.today())
        hours = self.employee.get_work_days_data(
            datetime.combine(today, time(
                0, 0, 0, 0)),
            datetime.combine(
                today, time(23, 59, 59, 99999)),
        )['hours']
        self.assertEqual(hours, 8.0)
