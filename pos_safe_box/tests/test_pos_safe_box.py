# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import odoo
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestPosSafeBox(TestPointOfSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.pos_config.cash_control = True
        cls.safe_box_group = cls.env["safe.box.group"].create(
            {
                "name": "Group",
                "code": "SB",
                "currency_id": cls.env.ref("base.USD").id,
            }
        )
        cls.coin_01 = cls.env["safe.box.coin"].create(
            {
                "safe_box_group_id": cls.safe_box_group.id,
                "name": "Coin",
                "type": "coin",
                "rate": 1,
            }
        )
        cls.coin_02 = cls.env["safe.box.coin"].create(
            {
                "safe_box_group_id": cls.safe_box_group.id,
                "name": "Note",
                "type": "note",
                "rate": 1,
            }
        )
        cls.safe_box_01 = cls.env["safe.box"].create(
            {"safe_box_group_id": cls.safe_box_group.id, "name": "SB 01"}
        )
        cls.safe_box_02 = cls.env["safe.box"].create(
            {"safe_box_group_id": cls.safe_box_group.id, "name": "SB 02"}
        )
        cls.safe_box_03 = cls.env["safe.box"].create(
            {"safe_box_group_id": cls.safe_box_group.id, "name": "SB 03"}
        )
        cls.account_01 = (
            cls.env["account.account"]
            .sudo()
            .create(
                {
                    "name": "Account 01",
                    "code": "001",
                    "company_id": cls.company.id,
                    "account_type": "asset_cash",
                    "safe_box_group_id": cls.safe_box_group.id,
                }
            )
        )
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", cls.company.id)],
            limit=1,
        )
        cls.pos_config.safe_box_group_id = cls.safe_box_group
        cls.invoice_out = cls.env["account.move"].create(
            {
                "partner_id": cls.partner4.id,
                "company_id": cls.company.id,
                "move_type": "out_invoice",
                "date": "2016-03-12",
                "invoice_date": "2016-03-12",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product3.id,
                            "name": "Producto de prueba",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "tax_ids": [],
                        },
                    )
                ],
            }
        )
        cls.invoice_out.action_post()

    def test_pos_safe_box(self):
        self.pos_config._action_to_open_ui()
        session = self.pos_config.current_session_id
        session.action_pos_session_open()
        wizard_context = session.button_show_wizard_pay_out_invoice()["context"]
        cash_in = self.env["cash.pay.invoice"].with_context(**wizard_context)
        with Form(cash_in) as form:
            form.invoice_id = self.invoice_out
            self.assertEqual(form.amount, 100)
        cash_in.browse(form.id).action_pay_invoice()

        # Set it as rescue in order to avoid extra moves
        session.rescue = True
        session.cash_register_balance_end_real = session.cash_register_balance_end
        session.cash_register_difference = 0.0

        session.action_pos_session_closing_control()
        session.flush_recordset()
        self.assertEqual(session.state, "closed")
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
