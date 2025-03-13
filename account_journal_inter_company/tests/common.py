# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime

from dateutil import relativedelta

from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInterCompany(AccountTestInvoicingCommon):
    @classmethod
    def _setup_context(cls):
        return dict(
            cls.env.context,
            tracking_disable=True,
            queue_job__no_delay=True,
        )

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env = cls.env(context=cls._setup_context())
        cls.company_1 = cls.company_data["company"]
        cls.company_2 = cls.company_data_2["company"]

    def create_inter_company(
        self,
        company_1,
        company_2,
        journal_1=False,
        journal_2=False,
        account_1=False,
        account_2=False,
    ):
        journal_obj = self.env["account.journal"]
        if not account_1:
            account_1 = self.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_2.name,
                    "code": "I%s" % company_2.id,
                    "company_id": company_1.id,
                    "account_type": "liability_current",
                }
            )
        if not journal_1:
            journal_1 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_1.name, company_2.name),
                    "code": "I{}{}".format(company_1.id, company_2.id),
                    "type": "general",
                    "company_id": company_1.id,
                }
            )
        if not account_2:
            account_2 = self.env["account.account"].create(
                {
                    "name": "Intercompany to %s" % company_1.name,
                    "code": "I%s" % company_1.id,
                    "company_id": company_2.id,
                    "account_type": "liability_current",
                }
            )
        if not journal_2:
            journal_2 = journal_obj.create(
                {
                    "name": "Journal from %s to %s" % (company_2.name, company_1.name),
                    "code": "I{}{}".format(company_2.id, company_1.id),
                    "type": "general",
                    "company_id": company_2.id,
                }
            )
        self.env["res.inter.company"].create(
            {
                "company_id": company_1.id,
                "related_company_id": company_2.id,
                "journal_id": journal_1.id,
                "account_id": account_1.id,
                "related_journal_id": journal_2.id,
                "related_account_id": account_2.id,
            }
        )

    @classmethod
    def create_invoice(cls, company, inv_type, partner, product):
        move_obj = cls.env["account.move"].with_company(company.id)
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
                ("account_type", "=", "liability_current"),
            ],
            limit=1,
        )
        invoice = cls.env["account.move"].create(
            {
                "company_id": company.id,
                "move_type": inv_type,
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
        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)
        invoice.invoice_date = date_invoice
        invoice.with_company(company.id)._post()
        return invoice
