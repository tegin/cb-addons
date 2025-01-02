# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPosCloseApproval(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config = cls.env["pos.config"].create(
            {
                "name": "PoS config",
                "payment_method_ids": [(0, 0, {"name": "Cash", "is_cash_count": True})],
            }
        )
        cls.session = False
        cls.account = cls.env["account.account"].create(
            {
                "name": "Receivable",
                "code": "RCV00",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.cash_journal = cls.env["account.journal"].create(
            {"name": "CASH journal", "type": "cash", "code": "CSH00"}
        )
        cls.cash_payment_method = cls.env["pos.payment.method"].create(
            {
                "name": "Cash Test",
                "journal_id": cls.cash_journal.id,
                "receivable_account_id": cls.account.id,
            }
        )
        cls.pos_config.write(
            {"payment_method_ids": [(6, 0, cls.cash_payment_method.ids)]}
        )

    def _open_session(self):
        self.pos_config._action_to_open_ui()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()

    def test_unicity(self):
        self._open_session()
        with self.assertRaises(ValidationError):
            self.env["pos.session"].create(
                {"config_id": self.pos_config.id, "user_id": self.env.uid}
            )

    def test_unicity_with_approval(self):
        self.pos_config.requires_approval = True
        self._open_session()
        with self.assertRaises(ValidationError):
            self.env["pos.session"].create(
                {"config_id": self.pos_config.id, "user_id": self.env.uid}
            )

    def test_unicity_when_closed(self):
        self.pos_config.requires_approval = True
        self._open_session()
        self.assertFalse(self.session.rescue)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.rescue)
        session = self.env["pos.session"].create(
            {"config_id": self.pos_config.id, "user_id": self.env.uid}
        )
        self.assertTrue(session)

    def test_normal_closing(self):
        self._open_session()
        self.session.action_pos_session_closing_control()
        self.session.flush_recordset()
        self.assertEqual(self.session.state, "closed")

    def test_validation(self):
        self.pos_config.requires_approval = True
        self._open_session()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        self.assertFalse(self.session.rescue)
        self.session.action_pos_session_closing_control()
        self.assertTrue(self.session.rescue)
        self.pos_config._action_to_open_ui()
        self.assertTrue(self.pos_config.current_session_id)
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.state, "closed")

    def test_wizard(self):
        account = self.env["account.account"].create(
            {
                "company_id": self.pos_config.company_id.id,
                "name": "Account",
                "code": "CODE",
                "account_type": "asset_prepayments",
            }
        )
        self._open_session()
        self.assertEqual(self.session.cash_register_total_entry_encoding, 0)
        wizard = (
            self.env["pos.cash.box"]
            .with_context(default_session_id=self.session.id)
            .create({"amount": 10, "reason": "Out"})
        )
        wizard.run()
        self.session.invalidate_recordset()
        self.assertGreater(self.session.cash_register_total_entry_encoding, 0)
        wizard = (
            self.env["pos.cash.box"]
            .with_context(default_session_id=self.session.id)
            .create({"move_type": "out", "amount": 10, "reason": "Out"})
        )
        wizard.run()
        self.session.invalidate_recordset()
        self.assertEqual(self.session.cash_register_total_entry_encoding, 0)
        line = self.session.statement_line_ids[0]
        self.env["account.bank.statement.line.account"].with_context(
            active_model="account.bank.statement.line", active_ids=line.ids
        ).create({"account_id": account.id}).run()
        self.assertEqual(account.id, line.account_id.id)
