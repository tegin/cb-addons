# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestPosChangeJournal(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref("base.main_company")
        self.bank_account = self.env["account.account"].create(
            {
                "name": "Bank account",
                "code": "5720BNK",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "user_type_id": self.browse_ref(
                    "account.data_account_type_liquidity"
                ).id,
            }
        )
        self.cash_account = self.env["account.account"].create(
            {
                "name": "Safe box account",
                "code": "572CSH",
                "company_id": self.company.id,
                "currency_id": self.company.currency_id.id,
                "user_type_id": self.browse_ref(
                    "account.data_account_type_liquidity"
                ).id,
            }
        )
        self.journal_1 = self.env["account.journal"].create(
            {
                "name": "Bank 01",
                "type": "bank",
                "code": "BK01",
                "journal_user": True,
                "default_debit_account_id": self.bank_account.id,
                "default_credit_account_id": self.bank_account.id,
            }
        )
        self.journal_2 = self.env["account.journal"].create(
            {
                "name": "Cash 01",
                "type": "cash",
                "code": "CASH01",
                "journal_user": True,
                "default_debit_account_id": self.cash_account.id,
                "default_credit_account_id": self.cash_account.id,
            }
        )
        pos_vals = (
            self.env["pos.config"]
            .with_context(company_id=self.company.id)
            .default_get(
                [
                    "journal_id",
                    "stock_location_id",
                    "invoice_journal_id",
                    "pricelist_id",
                ]
            )
        )
        pos_vals.update(
            {
                "name": "Config",
                "requires_approval": True,
                "company_id": self.company.id,
                "crm_team_id": False,
                "journal_ids": [
                    (6, 0, self.journal_1.ids + self.journal_2.ids)
                ],
            }
        )
        self.pos_config = self.env["pos.config"].create(pos_vals)
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()

    def test_wizard(self):
        journal = self.journal_1
        wizard = (
            self.env["cash.box.journal.in"]
            .with_context(
                active_model="pos.session", active_ids=self.session.ids
            )
            .create({"amount": 10, "name": "Out"})
        )
        wizard.journal_id = journal
        wizard.run()
        self.assertGreater(
            self.session.statement_ids.filtered(
                lambda r: r.journal_id.id == journal.id
            ).balance_end,
            0,
        )
        statement = self.session.statement_ids.filtered(
            lambda r: r.journal_id.id == journal.id
        )
        statement_2 = self.session.statement_ids.filtered(
            lambda r: r.journal_id == self.journal_2
        )
        self.assertTrue(statement.line_ids)
        self.assertEqual(len(statement.line_ids), 1)
        self.assertFalse(statement_2.line_ids)
        line = statement.line_ids[0]
        action = (
            self.env["account.bank.statement.line.change.journal"]
            .with_context(default_session_id=self.session.id)
            .create({"line_id": line.id, "journal_id": self.journal_2.id})
        )
        self.assertEqual(action.journal_ids, self.pos_config.journal_ids)
        action.run()
        self.assertEqual(line.journal_id, self.journal_2)
        statement = self.session.statement_ids.filtered(
            lambda r: r.journal_id == self.journal_2
        )
        self.assertTrue(statement.line_ids)
        statement = self.session.statement_ids.filtered(
            lambda r: r.journal_id == self.journal_1
        )
        self.assertFalse(statement.line_ids)
