# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import time
from odoo.tests.common import TransactionCase


class TestAssetManagementDepreciationPercentage(TransactionCase):

    def setUp(self):
        super(TestAssetManagementDepreciationPercentage, self).setUp()
        self.asset_model = self.env['account.asset']
        self.asset_profile_model = self.env['account.asset.profile']
        self.account_account_type_model = self.env['account.account.type']
        self.account_type_regular = self.account_account_type_model.create({
            'name': 'Test Regular',
            'type': 'other',
        })
        self.view_asset = self.asset_model.create({
            'type': 'view',
            'state': 'open',
            'name': 'view',
            'purchase_value': 0.0,
        })
        self.account = self.env['account.account'].create({
            'name': 'Test account',
            'code': 'TAC',
            'user_type_id': self.account_type_regular.id,
        })
        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TJ',
            'type': 'general',
        })
        self.profile = self.asset_profile_model.create({
            'parent_id': self.view_asset.id,
            'account_expense_depreciation_id': self.account.id,
            'account_asset_id': self.account.id,
            'account_depreciation_id': self.account.id,
            'journal_id': self.journal.id,
            'name': "Test",
        })
        self.fiscal_year = self.env['date.range'].create({
            'type_id': self.ref('account_fiscal_year.fiscalyear'),
            'name': 'FY',
            'date_start': time.strftime('2019-01-01'),
            'date_end': time.strftime('2019-01-01'),
        })

    def test_1_percentage_days_calc(self):
        """Prorata temporis depreciation with days calc option."""
        asset = self.asset_model.create({
            'name': 'test asset',
            'profile_id': self.profile.id,
            'purchase_value': 4000,
            'salvage_value': 0,
            'date_start': time.strftime('2003-01-01'),
            'method_time': 'percentage',
            'method_number': 0,
            'method_period': 'month',
            'prorata': False,
            'days_calc': True,
            'use_leap_years': False,
            'annual_percentage': 25.0,
            'use_percentage': True,
        })
        asset.compute_depreciation_board()
        asset.refresh()
        # 25% of 4000 is 1000.
        # At 25% depreciation, and starting at 2016-01-01 we will
        # depreciate in 4 years, therefore ending at 2016-12-31.
        # That makes 1461 days between start and end date. This forms the
        # basis for the daily amount to depreciate.
        days = 1461
        day_amount = 4000 / days
        # January has 31 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[1].amount,
            31 * day_amount, places=2)
        # February has 29 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[2].amount,
            28 * day_amount, places=2)
        # March has 29 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[3].amount,
            31 * day_amount, places=2)
        # April has 30 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[4].amount,
            30 * day_amount, places=2)
        # January has 31 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[13].amount,
            31 * day_amount, places=2)
        # February has 29 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[14].amount,
            29 * day_amount, places=2)
        # March has 29 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[15].amount,
            31 * day_amount, places=2)
        # April has 30 days
        self.assertAlmostEqual(
            asset.depreciation_line_ids[16].amount,
            30 * day_amount, places=2)
