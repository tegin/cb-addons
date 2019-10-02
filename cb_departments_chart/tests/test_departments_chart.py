# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase, HttpCase, HOST, PORT
import mock
import json


class TestCBDepartmentsChart(TransactionCase):
    def setUp(self):
        super(TestCBDepartmentsChart, self).setUp()

        Department = self.env["hr.department"]

        self.department_1 = Department.create({"name": "Dep1"})
        self.department_2 = Department.create(
            {"name": "Dep2", "parent_id": self.department_1.id}
        )
        self.department_3 = Department.create(
            {"name": "Dep3", "parent_id": self.department_2.id}
        )

    def test_department_child_count(self):
        self.department_1._compute_child_all_count()
        self.assertEqual(self.department_1.child_all_count, 2)
        self.department_1._compute_image_medium()


class TestCBDepartmentsChartHttp(HttpCase):
    def setUp(self):
        super(TestCBDepartmentsChartHttp, self).setUp()
        with self.cursor() as cr:
            env = self.env(cr)
            Department = env["hr.department"]
            employee = env["hr.employee"].create({"name": "Emp"})
            self.department_1 = Department.create(
                {"name": "Dep1", "manager_id": employee.id}
            )
            self.department_2 = Department.create(
                {"name": "Dep2", "parent_id": self.department_1.id}
            )
            self.department_3 = Department.create(
                {"name": "Dep3", "parent_id": self.department_2.id}
            )
        self.authenticate("admin", "admin")

    @mock.patch("odoo.http.WebRequest.validate_csrf", return_value=True)
    def test_departments_chart_controller(self, r):
        data = {"params": {"department_id": self.department_1.id}}
        url = "/cb_departments_chart/get_org_chart"
        url = "http://%s:%s%s" % (HOST, PORT, url)
        headers = {"Content-Type": "application/json"}
        data = json.dumps(data)
        response = self.opener.post(
            url, data=data, headers=headers, timeout=10
        )
        json_data = json.loads(response.text)
        self.assertEqual(json_data["result"]["self"]["name"], "Dep1")
        self.assertEqual(json_data["result"]["self"]["direct_sub_count"], 1)
        self.assertEqual(json_data["result"]["self"]["indirect_sub_count"], 2)
        self.assertEqual(json_data["result"]["children"][0]["name"], "Dep2")
