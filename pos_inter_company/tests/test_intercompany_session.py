# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account_journal_inter_company.tests import common
from odoo.exceptions import UserError
from odoo.tests import Form


class TestInterCompanyCashInvoice(common.TestInterCompany):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "service", "company_id": False}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "company_id": False}
        )

        cls.pos_config = cls.env["pos.config"].create({"name": "PoS config"})
        cls.out_invoice_company_1 = cls.create_invoice(
            cls.company_1, "out_invoice", cls.partner, cls.product
        )
        cls.out_invoice_company_2 = cls.create_invoice(
            cls.company_2, "out_invoice", cls.partner, cls.product
        )

        cls.pos_config.open_session_cb()
        cls.session = cls.pos_config.current_session_id
        cls.session.action_pos_session_open()
        out_invoice = cls.env["pos.box.cash.invoice.out"].with_context(
            active_ids=cls.session.ids,
            active_model="pos.session",
            default_session_id=cls.session.id,
        )
        with Form(out_invoice) as form:
            form.move_id = cls.out_invoice_company_1
        out_invoice.browse(form.id).run()

        out_invoice = cls.env["pos.box.cash.invoice.out"].with_context(
            active_ids=cls.session.ids,
            active_model="pos.session",
            default_session_id=cls.session.id,
        )
        with Form(out_invoice) as form:
            form.move_id = cls.out_invoice_company_2
        out_invoice.browse(form.id).run()

    def test_pos_inter_company_error(self):
        with self.assertRaises(UserError):
            self.session.action_pos_session_closing_control()

    def test_pos_inter_company(self):
        self.create_inter_company(self.company_1, self.company_2)
        self.assertFalse(self.session.inter_company_move_ids)
        self.session.action_pos_session_closing_control()
        self.assertEqual(self.out_invoice_company_1.amount_residual, 0)
        self.assertEqual(self.out_invoice_company_2.amount_residual, 0)
        related_moves = self.session._get_related_account_moves()
        self.assertIn(self.out_invoice_company_1, related_moves)
        self.assertIn(self.out_invoice_company_2, related_moves)
        self.assertTrue(self.session.inter_company_move_ids)
