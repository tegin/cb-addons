# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import SavepointCase


class TestInterCompany(SavepointCase):
    @classmethod
    def _setup_context(cls):
        return dict(
            cls.env.context,
            tracking_disable=True,
            test_queue_job_no_delay=True,
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=cls._setup_context())
        cls.company_1 = cls.env["res.company"].create(
            {
                "name": "1Company",
                "vat": "1",
                "currency_id": cls.env.ref("base.USD").id,
                "country_id": cls.env.ref("base.us").id,
                "logo": False,
            }
        )
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "2Company",
                "vat": "2",
                "currency_id": cls.env.ref("base.USD").id,
                "country_id": cls.env.ref("base.us").id,
                "logo": False,
            }
        )
        cls.chart_template_id = cls.env["account.chart.template"].search(
            [("visible", "=", True)], limit=1
        )
        for company in [cls.company_1, cls.company_2]:
            cls.env.user.write(
                {"company_ids": [(4, company.id)], "company_id": company.id}
            )
            cls.chart_template_id.try_loading()
        cls.user_type = cls.env.ref("account.data_account_type_revenue")

    def create_inter_company(
        self, company_1, company_2, journal_1=False, journal_2=False
    ):
        journal_obj = self.env["account.journal"]
        if not journal_1:
            account = self.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_2.name,
                    "code": "I;%s" % company_2.id,
                    "company_id": company_1.id,
                    "user_type_id": self.env.ref(
                        "account.data_account_type_liquidity"
                    ).id,
                }
            )
            journal_1 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_1.name, company_2.name),
                    "code": "I;{};{}".format(company_1.id, company_2.id),
                    "type": "general",
                    "company_id": company_1.id,
                    "default_account_id": account.id,
                }
            )
        if not journal_2:
            account = self.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_1.name,
                    "code": "I;%s" % company_1.id,
                    "company_id": company_2.id,
                    "user_type_id": self.env.ref(
                        "account.data_account_type_liquidity"
                    ).id,
                }
            )
            journal_2 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_2.name, company_1.name),
                    "code": "I;{};{}".format(company_2.id, company_1.id),
                    "type": "general",
                    "company_id": company_2.id,
                    "default_account_id": account.id,
                }
            )
        self.env["res.inter.company"].create(
            {
                "company_id": company_1.id,
                "related_company_id": company_2.id,
                "journal_id": journal_1.id,
                "related_journal_id": journal_2.id,
            }
        )

    @classmethod
    def create_invoice(cls, company, inv_type, partner, product):
        move_obj = cls.env["account.move"].with_context(force_company=company.id)
        if inv_type in move_obj.get_purchase_types():
            journal_type = "purchase"
        elif inv_type in move_obj.get_sale_types():
            journal_type = "sale"
        else:
            journal_type = "general"
        journal = cls.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", journal_type)],
            limit=1,
        )
        account = cls.env["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", cls.user_type.id),
            ],
            limit=1,
        )
        invoice = cls.env["account.move"].create(
            {
                "company_id": company.id,
                "type": inv_type,
                "partner_id": partner.id,
                "journal_id": journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": 100,
                            "name": product.name,
                            "account_id": account.id,
                        },
                    )
                ],
            }
        )
        invoice.with_context(force_company=company.id).post()
        return invoice
