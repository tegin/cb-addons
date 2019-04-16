import odoo.tests.common as common


class TestPersonalDays(common.TransactionCase):

    def setUp(self):
        super(TestPersonalDays, self).setUp()

        HolidaysStatus = self.env['hr.holidays.status']
        Employee = self.env['hr.employee']

        self.employee1 = Employee.create({
            'name': 'Employee 1',
        })
        self.status = HolidaysStatus.create({
            'name': 'Festivo Abril',
            'cb_personal_day': True,
            'ranges': [(0, 0, {
                'year': 2019,
                'date_from': '2019-04-01',
                'date_to': '2019-04-30',
            })]
        })

    def test_personal_days_warning(self):
        holiday1 = self.env['hr.holidays'].new({
            'date_from': '2019-04-20 10:00:00',
            'date_to': '2019-04-20 12:00:00',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee1.id,
            'type': 'remove',
        })
        holiday1._compute_warning_range()
        self.assertFalse(holiday1.warning)

        holiday2 = self.env['hr.holidays'].new({
            'date_from': '2019-04-20 10:00:00',
            'date_to': '2019-05-20 12:00:00',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee1.id,
            'type': 'remove',
        })
        holiday2._compute_warning_range()
        self.assertTrue(holiday2.warning)
        self.assertEqual(
            holiday2.warning,
            'The selected dates are out of'
            ' this holiday type\'s range. (2019-04-01 - 2019-04-30)')

    def test_personal_days_pending(self):
        allocation = self.env['hr.holidays'].create({
            'holiday_status_id': self.status.id,
            'holiday_type': 'employee',
            'employee_id': self.employee1.id,
            'type': 'add',
            'number_of_days_temp': 1
        })
        allocation.action_approve()
        self.status._compute_pending_employees()
        self.assertTrue(self.status.pending_employees_id)
        self.assertEqual(self.status.pending_employees_id[0], self.employee1)

        holiday = self.env['hr.holidays'].create({
            'date_from': '2019-04-23 10:00:00',
            'date_to': '2019-04-23 12:00:00',
            'holiday_status_id': self.status.id,
            'employee_id': self.employee1.id,
            'type': 'remove',
            'number_of_days_temp': 1
        })
        holiday.action_approve()
        self.status._compute_pending_employees()
        self.assertFalse(self.status.pending_employees_id)
