# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestInterCompany(SavepointCase):
    def setUp(self):
        super(TestInterCompany, self).setUp()
        self.company_1 = self.env["res.company"].create(
            {"name": "1Company", "vat": 1, "currency_id": self.ref("base.USD")}
        )
        self.company_2 = self.env["res.company"].create(
            {"name": "2Company", "vat": 2, "currency_id": self.ref("base.USD")}
        )
        self.chart_template_id = self.env["account.chart.template"].search(
            [("visible", "=", True)], limit=1
        )
        for company in [self.company_1, self.company_2]:
            self.env.user.write(
                {"company_ids": [(4, company.id)], "company_id": company.id}
            )
            self.chart_template_id.load_for_current_company(15.0, 15.0)

    def create_inter_company(
        self, company_1, company_2, journal_1=False, journal_2=False
    ):
        journal_obj = self.env["account.journal"]
        if not journal_1:
            journal_1 = journal_obj.search(
                [("company_id", "=", self.company_1.id)], limit=1
            )
        if not journal_2:
            journal_2 = journal_obj.search(
                [("company_id", "=", self.company_2.id)], limit=1
            )
        self.env["res.inter.company"].create(
            {
                "company_id": company_1.id,
                "related_company_id": company_2.id,
                "journal_id": journal_1.id,
                "related_journal_id": journal_2.id,
            }
        )
