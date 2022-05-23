import time
from datetime import datetime

from dateutil import relativedelta
from odoo import fields, tools
from odoo.modules.module import get_resource_path
from odoo.tests.common import Form, TransactionCase


class TestCreditControlDeferred(TransactionCase):
    def _load(self, module, *args):
        tools.convert_file(
            self.cr,
            module,
            get_resource_path(module, *args),
            {},
            "init",
            False,
            "test",
            self.registry._assertion_report,
        )

    def setUp(self):
        super().setUp()
        self._load("account", "test", "account_minimal_test.xml")

        journal = self.env.ref("account.sales_journal")

        account_type_rec = self.env.ref("account.data_account_type_receivable")
        self.account = self.env["account.account"].create(
            {
                "code": "TEST430001",
                "name": "Clients (test)",
                "user_type_id": account_type_rec.id,
                "reconcile": True,
            }
        )

        tag_operation = self.env.ref("account.account_tag_operating")
        account_type_inc = self.env.ref("account.data_account_type_revenue")
        analytic_account = self.env["account.account"].create(
            {
                "code": "TEST701001",
                "name": "Ventes en Belgique (test)",
                "user_type_id": account_type_inc.id,
                "reconcile": True,
                "tag_ids": [(6, 0, [tag_operation.id])],
            }
        )
        payment_term = self.env.ref("account.account_payment_term_immediate")

        product = self.env["product.product"].create({"name": "Product test"})

        self.policy = self.env["credit.control.policy"].create(
            {
                "name": "deferred",
                "account_ids": [(6, 0, [self.account.id])],
                "level_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Deferred",
                            "level": 1,
                            "channel": "email_deferred",
                            "computation_mode": "net_days",
                            "delay_days": 10,
                            "email_template_id": self.env.ref(
                                "account_credit_control."
                                "email_template_credit_control_base"
                            ).id,
                            "custom_text": "CUSTOM TEXT",
                            "custom_mail_text": "CUSTOM MAIL TEXT",
                        },
                    )
                ],
            }
        )
        self.policy.write({"account_ids": [(6, 0, [self.account.id])]})

        # There is a bug with Odoo ...
        # The field "credit_policy_id" is considered as an "old field" and
        # the field property_account_receivable_id like a "new field"
        # The ORM will create the record with old field
        # and update the record with new fields.
        # However constrains are applied after the first creation.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Partner",
                "property_account_receivable_id": self.account.id,
            }
        )
        self.partner_02 = self.env["res.partner"].create(
            {"name": "Partner 02", "parent_id": self.partner.id}
        )
        self.partner.credit_policy_id = self.policy.id

        date_invoice = datetime.today() - relativedelta.relativedelta(years=1)

        # Create an invoice
        invoice_form = Form(
            self.env["account.move"].with_context(
                default_type="out_invoice", check_move_validity=False
            )
        )
        invoice_form.invoice_date = date_invoice
        invoice_form.invoice_date_due = date_invoice
        invoice_form.partner_id = self.partner
        invoice_form.journal_id = journal
        invoice_form.invoice_payment_term_id = payment_term

        with invoice_form.invoice_line_ids.new() as invoice_line_form:
            invoice_line_form.product_id = product
            invoice_line_form.quantity = 1
            invoice_line_form.price_unit = 500
            invoice_line_form.account_id = analytic_account
            invoice_line_form.tax_ids.clear()
        self.invoice = invoice_form.save()

        self.invoice.post()

        self.user = self.env["res.users"].create(
            {"name": "Test user", "login": "test_user"}
        )

    def generate_run(self):
        control_run = self.env["credit.control.run"].create(
            {
                "date": fields.Date.today(),
                "policy_ids": [(6, 0, [self.policy.id])],
            }
        )
        control_run.with_context(lang="en_US").generate_credit_lines()

        self.assertTrue(len(self.invoice.credit_control_line_ids), 1)
        self.assertEqual(control_run.state, "done")
        control_lines = self.invoice.credit_control_line_ids
        marker = self.env["credit.control.marker"].create(
            {"name": "to_be_sent", "line_ids": [(6, 0, control_lines.ids)]}
        )
        marker.mark_lines()
        control_lines.flush()

        self.assertEqual(0, self.partner.credit_control_communication_count)
        control_run.run_channel_action()
        communications = control_run.line_ids.communication_id
        self.assertTrue(communications)
        self.assertEqual(communications.credit_control_line_ids, control_lines)
        self.assertEqual(1, len(communications.message_ids))
        self.assertEqual(1, self.partner.credit_control_communication_count)
        return control_run, control_lines, communications

    def test_credit_control_deferred(self):
        control_run, control_lines, communications = self.generate_run()
        action_mail = communications.action_communication_send()
        send_mail_action = (
            self.env[action_mail["res_model"]]
            .with_context(**action_mail["context"])
            .create({})
        )
        send_mail_action.send_mail()
        communications.refresh()
        self.assertEqual(communications.state, "sent")
        self.assertEqual(2, len(communications.message_ids))
        action_mail = communications.action_communication_answer()
        send_mail_action = (
            self.env[action_mail["res_model"]]
            .with_context(**action_mail["context"])
            .create({})
        )
        now = fields.Datetime.now()
        time.sleep(3)
        send_mail_action.send_mail()
        communications.refresh()
        self.assertEqual(3, len(communications.message_ids))
        self.assertGreater(communications.last_message, now)
        self.assertEqual(communications.total_due, self.invoice.amount_total)
        self.assertEqual(
            communications.total_invoiced, self.invoice.amount_total
        )
        partial_payment = self.env["account.move"].create(
            {
                "journal_id": self.env.ref("account.cash_journal").id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.env.ref("account.cash").id,
                            "debit": 100,
                        },
                    ),
                    (0, 0, {"account_id": self.account.id, "credit": 100}),
                ],
            }
        )
        partial_payment.post()
        (partial_payment.line_ids | self.invoice.line_ids).filtered(
            lambda r: r.account_id == self.account
        ).reconcile()
        self.invoice.refresh()
        communications.update_balance()
        communications.refresh()
        self.assertEqual(
            communications.total_due,
            self.invoice.amount_total - 100,
        )
        self.assertEqual(
            communications.total_invoiced, self.invoice.amount_total
        )

    def test_credit_control_deferred_manual(self):
        control_run, control_lines, communications = self.generate_run()
        self.assertEqual("queued", communications.state)
        communications.action_mark_as_sent()
        self.assertEqual("sent", communications.state)
        communications.action_mark_as_solved()
        self.assertEqual("solved", communications.state)

    def test_credit_control_deferred_user_01(self):
        self.partner.payment_responsible_id = False
        self.env.company.payment_responsible_id = self.user
        control_run, control_lines, communications = self.generate_run()
        self.assertEqual(communications.user_id, self.user)

    def test_credit_control_deferred_user_02(self):
        self.partner.payment_responsible_id = self.env.user
        self.env.company.payment_responsible_id = self.user
        control_run, control_lines, communications = self.generate_run()
        self.assertEqual(communications.user_id, self.env.user)

    def test_credit_control_deferred_contact_01(self):
        control_run, control_lines, communications = self.generate_run()
        self.assertEqual(communications.contact_address_id, self.partner)

    def test_credit_control_deferred_contact_02(self):
        self.partner.write(
            {"credit_control_contact_partner_id": self.partner_02.id}
        )
        control_run, control_lines, communications = self.generate_run()
        self.assertEqual(communications.contact_address_id, self.partner_02)
