# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, HttpCase, HOST, PORT
import mock
import json


class TestCBDepartmentsChart(TransactionCase):

    def setUp(self):
        super(TestCBDepartmentsChart, self).setUp()

        Department = self.env['hr.department']

        self.department_1 = Department.create({
            'name': 'Dep1'
        })
        self.department_2 = Department.create({
            'name': 'Dep2',
            'parent_id': self.department_1.id
        })
        self.department_3 = Department.create({
            'name': 'Dep3',
            'parent_id': self.department_2.id
        })

    def test_department_child_count(self):
        self.department_1._compute_child_all_count()
        self.assertEqual(self.department_1.child_all_count, 2)
        self.department_1._compute_image_medium()
