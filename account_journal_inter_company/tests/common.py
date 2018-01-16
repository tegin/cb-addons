# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestInterCompany(SavepointCase):

    def setUp(self):
        super(TestInterCompany, self).setUp()
        self.company_1 = self.env['res.company'].create({
            'name': 'Company 1',
            'vat': 1,
            'currency_id': self.ref('base.USD')
        })
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
            'vat': 2,
            'currency_id': self.ref('base.USD')
        })
        self.chart_template_id = self.env['account.chart.template'].search(
            [('visible', '=', True)], limit=1
        )
        for company in [self.company_1, self.company_2]:
            if not company.chart_template_id:
                wizard = self.env['wizard.multi.charts.accounts'].create({
                    'company_id': company.id,
                    'chart_template_id': self.chart_template_id.id,
                    'transfer_account_id':
                        self.chart_template_id.transfer_account_id.id,
                    'code_digits': 6,
                    'sale_tax_rate': 15.0,
                    'purchase_tax_rate': 15.0,
                    'complete_tax_set':
                        self.chart_template_id.complete_tax_set,
                    'currency_id': company.currency_id.id,
                    'bank_account_code_prefix':
                        self.chart_template_id.bank_account_code_prefix,
                    'cash_account_code_prefix':
                        self.chart_template_id.cash_account_code_prefix,
                })
                wizard.onchange_chart_template_id()
                wizard.execute()

    def create_inter_company(self, company_1, company_2,
                             journal_1=False, journal_2=False):
        journal_obj = self.env['account.journal']
        if not journal_1:
            journal_1 = journal_obj.search(
                [('company_id', '=', self.company_1.id)], limit=1
            )
        if not journal_2:
            journal_2 = journal_obj.search(
                [('company_id', '=', self.company_2.id)], limit=1
            )
        self.env['res.inter.company'].create({
            'company_id': company_1.id,
            'related_company_id': company_2.id,
            'journal_id': journal_1.id,
            'related_journal_id': journal_2.id,
        })
