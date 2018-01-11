# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPosCloseApproval(TransactionCase):
    def setUp(self):
        super(TestPosCloseApproval, self).setUp()
        self.pos_config = self.env['pos.config'].create({'name': 'PoS config'})
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()

    def test_unicity(self):
        with self.assertRaises(ValidationError):
            self.env['pos.session'].create({
                'config_id': self.pos_config.id,
                'user_id': self.env.uid,
            })

    def test_unicity_with_approval(self):
        self.pos_config.requires_approval = True
        with self.assertRaises(ValidationError):
            self.env['pos.session'].create({
                'config_id': self.pos_config.id,
                'user_id': self.env.uid,
            })

    def test_unicity_when_closed(self):
        self.pos_config.requires_approval = True
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.session.state, 'pending_approval')
        session = self.env['pos.session'].create({
            'config_id': self.pos_config.id,
            'user_id': self.env.uid,
        })
        self.assertTrue(session)

    def test_normal_closing(self):
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.session.state, 'closed')

    def test_validation(self):
        self.pos_config.requires_approval = True
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.session.action_pos_session_open()
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.session.state, 'pending_approval')
        self.pos_config.open_session_cb()
        self.assertTrue(self.pos_config.current_session_id)
        self.session.action_pos_session_approve()
        self.assertEqual(self.session.state, 'closed')

    def test_wizard(self):
        journal = self.session.journal_ids[0]
        account = self.env['account.account'].create({
            'company_id': self.pos_config.company_id.id,
            'name': 'Account',
            'code': 'CODE',
            'user_type_id': self.ref('account.data_account_type_prepayments')
        })
        wizard = self.env['cash.box.journal.in'].with_context(
            active_model='pos.session', active_ids=self.session.ids
        ).create({
            'amount': 10,
            'name': 'Out'
        })
        wizard.journal_id = journal
        wizard.run()
        self.assertGreater(
            self.session.statement_ids.filtered(
                lambda r: r.journal_id.id == journal.id
            ).balance_end, 0
        )
        wizard = self.env['cash.box.journal.out'].with_context(
            active_model='pos.session', active_ids=self.session.ids
        ).create({
            'amount': 10,
            'name': 'Out'
        })
        wizard.journal_id = journal
        wizard.run()
        self.assertEqual(
            self.session.statement_ids.filtered(
                lambda r: r.journal_id.id == journal.id
            ).balance_end, 0
        )
        statement = self.session.statement_ids.filtered(
            lambda r: r.journal_id.id == journal.id
        )
        line = statement.line_ids[0]
        self.env['account.bank.statement.line.account'].with_context(
            active_model='account.bank.statement.line', active_ids=line.ids
        ).create({
            'account_id': account.id
        }).run()
        self.assertEqual(account.id, line.account_id.id)
