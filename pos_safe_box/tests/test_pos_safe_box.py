# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPosSafeBox(TransactionCase):
    def setUp(self):
        super(TestPosSafeBox, self).setUp()
        self.safe_box_group = self.env["safe.box.group"].create(
            {
                "name": "Group",
                "code": "SB",
                "currency_id": self.ref("base.USD"),
            }
        )
        self.coin_01 = self.env["safe.box.coin"].create(
            {
                "safe_box_group_id": self.safe_box_group.id,
                "name": "Coin",
                "type": "coin",
                "rate": 1,
            }
        )
        self.coin_02 = self.env["safe.box.coin"].create(
            {
                "safe_box_group_id": self.safe_box_group.id,
                "name": "Note",
                "type": "note",
                "rate": 1,
            }
        )
        self.safe_box_01 = self.env["safe.box"].create(
            {"safe_box_group_id": self.safe_box_group.id, "name": "SB 01"}
        )
        self.safe_box_02 = self.env["safe.box"].create(
            {"safe_box_group_id": self.safe_box_group.id, "name": "SB 02"}
        )
        self.safe_box_03 = self.env["safe.box"].create(
            {"safe_box_group_id": self.safe_box_group.id, "name": "SB 03"}
        )
        self.company = self.browse_ref("base.main_company")
        self.account_01 = self.env["account.account"].create(
            {
                "name": "Account 01",
                "code": "001",
                "company_id": self.company.id,
                "user_type_id": self.ref(
                    "account.data_account_type_liquidity"
                ),
                "safe_box_group_id": self.safe_box_group.id,
            }
        )
        self.journal = self.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", self.company.id)],
            limit=1,
        )
        self.pos_config = self.env["pos.config"].new(
            {
                "company_id": self.company.id,
                "safe_box_group_id": self.safe_box_group.id,
                "name": "Safe Box PoS",
                "requires_approval": False,
            }
        )
        self.pos_config = self.pos_config.create(self.pos_config._cache)

    def test_pos_safe_box(self):
        self.pos_config.open_session_cb()
        session = self.pos_config.current_session_id
        self.assertTrue(session.statement_ids)
        self.env["cash.box.out"].with_context(
            active_model="pos.session", active_ids=session.ids
        ).create({"name": "Testing", "amount": 100}).run()
        session.action_pos_session_closing_control()
        self.assertTrue(session.pos_session_validation_id)
        validation = session.pos_session_validation_id
        with self.assertRaises(ValidationError):
            validation.close()
        validation.line_ids.filtered(
            lambda r: r.safe_box_coin_id == self.coin_01
        ).value = 50
        validation.line_ids.filtered(
            lambda r: r.safe_box_coin_id == self.coin_02
        ).value = 50
        with self.assertRaises(ValidationError):
            validation.close()
        self.safe_box_group.write(
            {
                "coin_safe_box_id": self.safe_box_01.id,
                "note_safe_box_id": self.safe_box_02.id,
                "approve_note_safe_box_id": self.safe_box_03.id,
            }
        )
        validation.close()
        self.assertEqual(self.safe_box_01.amount, 50)
        self.assertEqual(self.safe_box_02.amount, 50)
        self.assertEqual(self.safe_box_03.amount, 0)
        with self.assertRaises(ValidationError):
            validation.close()
        validation.approve()
        self.assertEqual(self.safe_box_01.amount, 50)
        self.assertEqual(self.safe_box_02.amount, 0)
        self.assertEqual(self.safe_box_03.amount, 50)
        with self.assertRaises(ValidationError):
            validation.approve()
