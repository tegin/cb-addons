import time

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class ThirdParty(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.browse_ref("base.main_company")
        self.journal = self.env["account.journal"].create(
            {
                "name": "Journal",
                "company_id": self.company.id,
                "code": "TPJ",
                "type": "general",
            }
        )
        self.transfer_acc = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "Tra",
                "name": "Transfer Account",
                "user_type_id": self.browse_ref(
                    "account.data_account_type_current_assets"
                ).id,
                "reconcile": False,
            }
        )
        self.customer_acc = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "ThirdPartyCust",
                "name": "Third party customer account",
                "user_type_id": self.browse_ref(
                    "account.data_account_type_receivable"
                ).id,
                "reconcile": True,
            }
        )

        self.customer_acc2 = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "ThirdPartyCust2",
                "name": "Third party customer account2",
                "user_type_id": self.browse_ref(
                    "account.data_account_type_receivable"
                ).id,
                "reconcile": True,
            }
        )
        self.supplier_acc = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "code": "ThirdPartySupp",
                "name": "Third party supplier account",
                "user_type_id": self.browse_ref(
                    "account.data_account_type_payable"
                ).id,
                "reconcile": True,
            }
        )
        self.supplier = self.env["res.partner"].create(
            {
                "name": "supplier",
                "supplier_rank": 1,
                "third_party_sequence_prefix": "SUP",
            }
        )
        self.supplier_2 = self.env["res.partner"].create(
            {"name": "supplier 2", "supplier_rank": 1}
        )
        self.customer = self.env["res.partner"].create(
            {"name": "Customer", "customer_rank": 1}
        )
        self.product = self.env["product.product"].create(
            {"type": "service", "name": "Product"}
        )
        self.third_party_taxes = self.env["account.tax"].create(
            {
                "company_id": self.company.id,
                "name": "Supplier Tax",
                "amount": 20,
                "type_tax_use": "sale",
            }
        )
        self.tax = self.env["account.tax"].create(
            {
                "company_id": self.company.id,
                "name": "Tax",
                "amount": 10,
                "type_tax_use": "sale",
            }
        )
        self.third_party_product = self.env["product.product"].create(
            {
                "type": "service",
                "name": "Third party product",
                "taxes_id": [(6, 0, self.third_party_taxes.ids)],
            }
        )
        self.product = self.env["product.product"].create(
            {
                "type": "service",
                "name": "Product",
                "taxes_id": [(6, 0, self.tax.ids)],
            }
        )

    def test_multicompany(self):
        self.assertFalse(self.company.default_third_party_customer_account_id)
        self.assertFalse(self.company.default_third_party_supplier_account_id)
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        self.company.refresh()
        self.assertEqual(
            self.company.default_third_party_customer_account_id,
            self.customer.property_third_party_customer_account_id,
        )
        self.assertEqual(
            self.company.default_third_party_supplier_account_id,
            self.customer.property_third_party_supplier_account_id,
        )
        prop = self.customer.property_ids.filtered(
            lambda r: r.company_id == self.company
        )
        prop.write(
            {"property_third_party_customer_account_id": self.customer_acc2.id}
        )
        prop.refresh()
        self.assertEqual(
            self.customer.with_context(
                force_company=self.company.id
            ).property_third_party_customer_account_id,
            self.customer_acc2,
        )
        self.assertEqual(
            self.customer.with_context(
                force_company=self.company.id
            ).property_third_party_customer_account_id,
            prop.property_third_party_customer_account_id,
        )

    def test_create_partner_third_party(self):
        third_party = self.env["res.partner"].create(
            {
                "name": "supplier",
                "supplier_rank": 1,
                "third_party_sequence_prefix": "SUP",
            }
        )
        self.assertTrue(third_party.third_party_sequence_id)
        self.assertEqual(third_party.third_party_sequence_id.prefix, "SUP")
        self.assertFalse(third_party.third_party_sequence_id.company_id)
        third_party.third_party_sequence_prefix = "SUP2"
        self.assertEqual(third_party.third_party_sequence_id.prefix, "SUP2")

    def test_raising_error(self):
        self.company.write({"third_party_journal_id": self.journal.id})
        sale_order = self.env["sale.order"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.customer.id,
                "third_party_order": True,
                "third_party_partner_id": self.supplier_2.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "third_party_product_id": self.third_party_product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                            "third_party_price": 10,
                            "tax_id": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        with self.assertRaises(UserError):
            # raises: Please a Third Party sequence
            sale_order.action_confirm()
        self.supplier_2.write({"third_party_sequence_prefix": "SUP"})
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": False,
            }
        )
        with self.assertRaises(UserError):
            # raises: Please define a third party supplier account
            sale_order.action_confirm()
        self.company.write(
            {
                "default_third_party_customer_account_id": False,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        with self.assertRaises(UserError):
            # raises: Please define a third party customer account
            sale_order.action_confirm()

    def test_cancel_third_party(self):
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
                "third_party_journal_id": self.journal.id,
            }
        )
        sale_order = self.env["sale.order"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.customer.id,
                "third_party_order": True,
                "third_party_partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "third_party_product_id": self.third_party_product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                            "third_party_price": 10,
                            "tax_id": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        self.assertEqual(
            sale_order.action_view_third_party_order()["res_id"],
            sale_order.third_party_order_ids.id,
        )
        self.assertTrue(sale_order.third_party_move_id)
        sale_order.with_context(force_delete=True).action_cancel()
        self.assertFalse(sale_order.third_party_move_id)

    def test_third_party_raises(self):
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "company_id": self.company.id,
                    "partner_id": self.customer.id,
                    "third_party_order": True,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "third_party_product_id": self.third_party_product.id,
                                "product_uom": self.product.uom_id.id,
                                "product_uom_qty": 1,
                                "price_unit": 100,
                                "third_party_price": 10,
                                "tax_id": [(6, 0, self.tax.ids)],
                            },
                        )
                    ],
                }
            )

    def test_third_party_security(self):
        user = self.env["res.users"].create(
            {
                "login": "demo_user_test",
                "name": "Demo User",
                "email": "demo@demo.de",
                "notification_type": "inbox",
                "groups_id": [
                    (
                        4,
                        self.browse_ref("sales_team.group_sale_salesman").id,
                    )
                ],
            }
        )
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        self.company.refresh()
        sale_order = (
            self.env["sale.order"]
            .with_user(user)
            .create(
                {
                    "company_id": self.company.id,
                    "partner_id": self.customer.id,
                    "third_party_order": True,
                    "third_party_partner_id": self.supplier.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "third_party_product_id": self.third_party_product.id,
                                "product_uom": self.product.uom_id.id,
                                "product_uom_qty": 1,
                                "price_unit": 100,
                                "third_party_price": 10,
                                "tax_id": [(6, 0, self.tax.ids)],
                            },
                        )
                    ],
                }
            )
        )
        self.assertEqual(0, sale_order.invoice_count)
        self.assertEqual(0, sale_order.third_party_order_count)
        self.assertEqual("no", sale_order.invoice_status)
        self.assertFalse(sale_order.third_party_move_id)
        sale_order.action_confirm()
        sale_order.third_party_move_id.check_access_rights("read")
        sale_order.third_party_move_id.check_access_rule("read")
        self.assertTrue(sale_order.third_party_move_id)
        self.assertEqual(1, sale_order.third_party_order_count)
        self.assertEqual("no", sale_order.invoice_status)
        self.assertEqual(len(sale_order.third_party_order_ids), 1)
        third_party_order = sale_order.third_party_order_ids[0]
        self.assertEqual(
            third_party_order.partner_id, sale_order.third_party_partner_id
        )
        self.assertEqual(sale_order.amount_total, 110)
        self.assertTrue(sale_order.third_party_move_id)
        self.assertEqual(sale_order.third_party_customer_in_residual, 110)
        self.assertEqual(sale_order.third_party_customer_out_residual, 110)
        self.assertEqual(sale_order.third_party_customer_in_state, "pending")
        self.assertEqual(sale_order.third_party_customer_out_state, "pending")
        self.assertEqual(sale_order.state, "done")
        journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id)], limit=1
        )
        statement = self.env["account.bank.statement"].create(
            {"name": "Statement", "journal_id": journal.id}
        )
        wizard = (
            self.env["cash.third.party.sale"]
            .with_context(
                active_ids=statement.ids, active_model=statement._name
            )
            .create({"sale_order_id": sale_order.id, "amount": 0})
        )
        wizard._onchange_sale_order()
        self.assertEqual(wizard.amount, sale_order.amount_total)
        wizard.amount = 100
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_in_residual, 10)
        self.assertEqual(sale_order.third_party_customer_in_state, "pending")
        statement = self.env["account.bank.statement"].create(
            {"name": "Statement", "journal_id": journal.id}
        )
        wizard = (
            self.env["cash.third.party.sale"]
            .with_context(
                active_ids=statement.ids, active_model=statement._name
            )
            .create({"sale_order_id": sale_order.id, "amount": 0})
        )
        wizard._onchange_sale_order()
        self.assertEqual(
            wizard.amount, sale_order.third_party_customer_in_residual
        )
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_in_state, "paid")
        # Test the outbound payment
        bank_journal = self.env["account.journal"].create(
            {
                "name": "Bank Test",
                "code": "BNKT",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "partner_type": "supplier",
                "partner_id": self.supplier.id,
                "amount": sale_order.third_party_customer_out_residual,
                "currency_id": self.company.currency_id.id,
                "payment_date": time.strftime("%Y") + "-01-05",
                "journal_id": bank_journal.id,
                "use_third_party_account": True,
            }
        )
        payment.post()
        supplier_acc = payment.partner_id.with_context(
            force_company=self.company.id
        ).property_third_party_supplier_account_id
        aml_recs = payment.move_line_ids.filtered(
            lambda l: l.account_id == supplier_acc
        )
        aml_recs += sale_order.third_party_move_id.line_ids.filtered(
            lambda l: l.partner_id == self.supplier
        )
        aml_recs.reconcile()
        self.assertEqual(sale_order.third_party_customer_out_residual, 0.0)
        self.assertEqual(sale_order.third_party_customer_out_state, "paid")

    def test_third_party(self):
        self.company.write(
            {
                "default_third_party_customer_account_id": self.customer_acc.id,
                "default_third_party_supplier_account_id": self.supplier_acc.id,
            }
        )
        self.company.refresh()
        sale_order = self.env["sale.order"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.customer.id,
                "third_party_order": True,
                "third_party_partner_id": self.supplier.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "third_party_product_id": self.third_party_product.id,
                            "product_uom": self.product.uom_id.id,
                            "product_uom_qty": 1,
                            "price_unit": 100,
                            "third_party_price": 10,
                            "tax_id": [(6, 0, self.tax.ids)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(0, sale_order.invoice_count)
        self.assertEqual(0, sale_order.third_party_order_count)
        self.assertEqual("no", sale_order.invoice_status)
        self.assertFalse(sale_order.third_party_move_id)
        sale_order.action_confirm()
        self.assertTrue(sale_order.third_party_move_id)
        self.assertEqual(1, sale_order.third_party_order_count)
        self.assertEqual("no", sale_order.invoice_status)
        self.assertEqual(len(sale_order.third_party_order_ids), 1)
        third_party_order = sale_order.third_party_order_ids[0]
        self.assertEqual(
            third_party_order.partner_id, sale_order.third_party_partner_id
        )
        self.assertEqual(sale_order.amount_total, 110)
        self.assertTrue(sale_order.third_party_move_id)
        self.assertEqual(sale_order.third_party_customer_in_residual, 110)
        self.assertEqual(sale_order.third_party_customer_out_residual, 110)
        self.assertEqual(sale_order.third_party_customer_in_state, "pending")
        self.assertEqual(sale_order.third_party_customer_out_state, "pending")
        self.assertEqual(sale_order.state, "done")
        journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id)], limit=1
        )
        statement = self.env["account.bank.statement"].create(
            {"name": "Statement", "journal_id": journal.id}
        )
        wizard = (
            self.env["cash.third.party.sale"]
            .with_context(
                active_ids=statement.ids, active_model=statement._name
            )
            .create({"sale_order_id": sale_order.id, "amount": 0})
        )
        wizard._onchange_sale_order()
        self.assertEqual(wizard.amount, sale_order.amount_total)
        wizard.amount = 100
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_in_residual, 10)
        self.assertEqual(sale_order.third_party_customer_in_state, "pending")
        statement = self.env["account.bank.statement"].create(
            {"name": "Statement", "journal_id": journal.id}
        )
        wizard = (
            self.env["cash.third.party.sale"]
            .with_context(
                active_ids=statement.ids, active_model=statement._name
            )
            .create({"sale_order_id": sale_order.id, "amount": 0})
        )
        wizard._onchange_sale_order()
        self.assertEqual(
            wizard.amount, sale_order.third_party_customer_in_residual
        )
        wizard.run()
        statement.balance_end_real = statement.balance_end
        statement.check_confirm_bank()
        self.assertEqual(sale_order.third_party_customer_in_state, "paid")
        # Test the outbound payment
        bank_journal = self.env["account.journal"].create(
            {
                "name": "Bank Test",
                "code": "BNKT",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "partner_type": "supplier",
                "partner_id": self.supplier.id,
                "amount": sale_order.third_party_customer_out_residual,
                "currency_id": self.company.currency_id.id,
                "payment_date": time.strftime("%Y") + "-01-05",
                "journal_id": bank_journal.id,
                "use_third_party_account": True,
            }
        )
        payment.post()
        supplier_acc = payment.partner_id.with_context(
            force_company=self.company.id
        ).property_third_party_supplier_account_id
        aml_recs = payment.move_line_ids.filtered(
            lambda l: l.account_id == supplier_acc
        )
        aml_recs += sale_order.third_party_move_id.line_ids.filtered(
            lambda l: l.partner_id == self.supplier
        )
        aml_recs.reconcile()
        self.assertEqual(sale_order.third_party_customer_out_residual, 0.0)
        self.assertEqual(sale_order.third_party_customer_out_state, "paid")

    def test_onchange_payment(self):
        payment = self.env["account.payment"].new(
            {"payment_type": "outbound", "use_third_party_account": True}
        )
        payment.payment_type = "transfer"
        payment._onchange_payment_type()
        self.assertFalse(payment.use_third_party_account)
