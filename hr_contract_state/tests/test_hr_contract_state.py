# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from mock import patch


class TestHrContractState(TransactionCase):

    def setUp(self):
        super(TestHrContractState, self).setUp()
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee'
        })
        self.contract = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'wage': 1000,
            'date_start': '2019-06-06',
        })
        self.company = self.env.user.company_id

    def test_hr_contract_state(self):
        with patch('odoo.fields.Date.today') as p:
            p.return_value = '2019-06-15'
            self.assertEqual(self.contract.state, 'draft')

            self.contract.update({'date_start': '2019-06-06'})
            self.env['hr.contract'].with_context(
                execute_old_update=True).update_state()
            self.assertEqual(self.contract.state, 'open')

            self.contract.write({'date_end': '2019-06-25'})
            self.assertEqual(self.contract.state, 'pending')

            self.contract.pending2to_expire()
            self.assertEqual(self.contract.state, 'to_expire')

            self.contract.renew_contract()
            renewed_contract = self.env['hr.contract'].browse(
                self.contract.renewed_contract_id)
            self.assertTrue(renewed_contract)
            self.assertEqual(self.contract.state, 'renewed')

            self.contract.write({'date_end': '2019-06-14'})
            self.assertEqual(self.contract.state, 'close')
