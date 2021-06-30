# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestPointOfSaleCommon(TransactionCase):
    def setUp(self):
        super(TestPointOfSaleCommon, self).setUp()
        self.AccountBankStatement = self.env["account.bank.statement"]
        self.AccountBankStatementLine = self.env["account.bank.statement.line"]
        self.PosMakePayment = self.env["pos.make.payment"]
        self.PosOrder = self.env["pos.order"]
        self.PosSession = self.env["pos.session"]
        self.company = self.env.ref("base.main_company")
        self.company_id = self.company.id
        coa = self.env["account.chart.template"].search(
            [("currency_id", "=", self.company.currency_id.id)], limit=1
        )
        test_sale_journal = self.env["account.journal"].create(
            {
                "name": "Sales Journal - Test",
                "code": "TSJ",
                "type": "sale",
                "company_id": self.company_id,
            }
        )
        self.company.write(
            {
                "anglo_saxon_accounting": coa.use_anglo_saxon,
                "bank_account_code_prefix": coa.bank_account_code_prefix,
                "cash_account_code_prefix": coa.cash_account_code_prefix,
                "transfer_account_code_prefix": coa.transfer_account_code_prefix,
                "chart_template_id": coa.id,
            }
        )
        self.product3 = self.env.ref("product.product_product_3")
        self.product4 = self.env.ref("product.product_product_4")
        self.partner1 = self.env.ref("base.res_partner_1")
        self.partner4 = self.env.ref("base.res_partner_4")
        self.pos_config = self.env.ref("point_of_sale.pos_config_main")
        self.pos_config.write(
            {
                "journal_id": test_sale_journal.id,
                "invoice_journal_id": test_sale_journal.id,
            }
        )
        self.led_lamp = self.env.ref("point_of_sale.led_lamp")
        self.whiteboard_pen = self.env.ref("point_of_sale.whiteboard_pen")
        self.newspaper_rack = self.env.ref("point_of_sale.newspaper_rack")

        self.cash_payment_method = self.pos_config.payment_method_ids.filtered(
            lambda pm: pm.name == "Cash"
        )
        self.bank_payment_method = self.pos_config.payment_method_ids.filtered(
            lambda pm: pm.name == "Bank"
        )
        account = self.company.account_default_pos_receivable_account_id
        self.credit_payment_method = self.env["pos.payment.method"].create(
            {
                "name": "Credit",
                "receivable_account_id": account.id,
                "split_transactions": True,
            }
        )
        self.pos_config.write(
            {"payment_method_ids": [(4, self.credit_payment_method.id)]}
        )

        # create a VAT tax of 10%, included in the public price
        Tax = self.env["account.tax"]
        account_tax_10_incl = Tax.create(
            {
                "name": "VAT 10 perc Incl",
                "amount_type": "percent",
                "amount": 10.0,
                "price_include": 1,
            }
        )

        # assign this 10 percent tax on the [PCSC234] PC Assemble SC234 product
        # as a sale tax
        self.product3.taxes_id = [(6, 0, [account_tax_10_incl.id])]

        # create a VAT tax of 5%, which is added to the public price
        account_tax_05_incl = Tax.create(
            {
                "name": "VAT 5 perc Incl",
                "amount_type": "percent",
                "amount": 5.0,
                "price_include": 0,
            }
        )

        # create a second VAT tax of 5% but this time for a child company, to
        # ensure that only product taxes of the current session's company are considered
        # (this tax should be ignore when computing order's taxes in following tests)
        account_tax_05_incl_chicago = Tax.with_context(
            default_company_id=self.ref("stock.res_company_1")
        ).create(
            {
                "name": "VAT 05 perc Excl (US)",
                "amount_type": "percent",
                "amount": 5.0,
                "price_include": 0,
            }
        )

        self.product4.company_id = False
        # I assign those 5 percent taxes on the PCSC349 product as a sale taxes
        self.product4.write(
            {
                "taxes_id": [
                    (
                        6,
                        0,
                        [
                            account_tax_05_incl.id,
                            account_tax_05_incl_chicago.id,
                        ],
                    )
                ]
            }
        )

        # Set account_id in the generated repartition lines.
        # Automatically, nothing is set.
        invoice_rep_lines = (account_tax_05_incl | account_tax_10_incl).mapped(
            "invoice_repartition_line_ids"
        )
        refund_rep_lines = (account_tax_05_incl | account_tax_10_incl).mapped(
            "refund_repartition_line_ids"
        )

        tax_received_account = self.company.account_sale_tax_id.mapped(
            "invoice_repartition_line_ids.account_id"
        )
        (invoice_rep_lines | refund_rep_lines).write(
            {"account_id": tax_received_account.id}
        )
        invoice_rep_lines = account_tax_05_incl_chicago.mapped(
            "invoice_repartition_line_ids"
        )
        refund_rep_lines = account_tax_05_incl_chicago.mapped(
            "refund_repartition_line_ids"
        )

        tax_received_account = self.env.ref(
            "stock.res_company_1"
        ).account_sale_tax_id.mapped("invoice_repartition_line_ids.account_id")
        (invoice_rep_lines | refund_rep_lines).write(
            {"account_id": tax_received_account.id}
        )


class TestManualOrder(TestPointOfSaleCommon):
    def setUp(self):
        super().setUp()
        self.product3 = self.env["product.product"].create(
            {"name": "TEST PRODUCT", "type": "service", "taxes_id": []}
        )
        self.product4 = self.env["product.product"].create(
            {"name": "TEST PRODUCT 4", "type": "service", "taxes_id": []}
        )
        self.pos_config.open_session_cb()
        self.pos_order_session0 = self.pos_config.current_session_id

    def test_manual_order_excluded(self):
        session = self.pos_order_session0
        self.assertTrue(session.config_id.pricelist_id)
        self.assertFalse(session.order_ids)
        wizard = self.env["pos.session.add.order"].create(
            {
                "session_id": session.id,
                "price": 10,
                "product_id": self.product4.id,
                "payment_method_id": session.payment_method_ids.ids[0],
            }
        )
        self.assertTrue(wizard)
        wizard.run()
        self.assertTrue(session.order_ids)
        self.assertEqual(1, len(session.order_ids))
        self.assertEqual(10, session.order_ids.lines.price_subtotal)

    def test_manual_order_included(self):
        session = self.pos_order_session0
        self.assertTrue(session.config_id.pricelist_id)
        self.assertFalse(session.order_ids)
        wizard = self.env["pos.session.add.order"].create(
            {
                "session_id": session.id,
                "price": 10,
                "product_id": self.product3.id,
                "payment_method_id": session.payment_method_ids.ids[0],
            }
        )
        self.assertTrue(wizard)
        wizard.run()
        self.assertTrue(session.order_ids)
        self.assertEqual(1, len(session.order_ids))
        self.assertEqual(10, session.order_ids.lines.price_subtotal_incl)

    def test_onchange_product(self):
        session = self.pos_order_session0
        self.product3.lst_price = 10
        with Form(self.env["pos.session.add.order"]) as wizard:
            wizard.session_id = session
            wizard.qty = 1
            wizard.payment_method_id = session.payment_method_ids[0]
            self.assertEqual(0, wizard.price)
            self.assertEqual(0, wizard.amount_total)
            wizard.product_id = self.product3
            self.assertNotEqual(0, wizard.price)
            self.assertNotEqual(0, wizard.amount_total)
