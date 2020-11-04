# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError

from . import common


class TestInterCompanyJournal(common.TestInterCompany):
    def test_intercompany(self):
        self.create_inter_company(self.company_1, self.company_2)
        self.assertTrue(self.company_1.inter_company_ids)
        self.assertTrue(self.company_2.inter_company_ids)
        self.assertEqual(
            self.company_1.inter_company_ids.inter_company_id,
            self.company_2.inter_company_ids,
        )
        self.assertTrue(
            self.company_1.related_company_ids.filtered(
                lambda r: r.id == self.company_2.id
            )
        )
        with self.assertRaises(ValidationError):
            self.create_inter_company(self.company_1, self.company_2)
