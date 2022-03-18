# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class PosSession(models.Model):
    _inherit = "pos.session"

    inter_company_move_ids = fields.One2many(
        "account.move", inverse_name="inter_company_pos_session_id"
    )

    def _pos_session_process_order(self, order, data):
        key = order.partner_id
        invoice_receivables = data["invoice_receivables"]
        inter_company_receivables = data["inter_company_invoice_receivables"]
        inter_company_amounts = data["inter_company_amounts"]
        if (
            order.is_invoiced
            and order.account_move.company_id == self.company_id
        ):
            # Combine invoice receivable lines
            key = key.with_context(force_company=self.company_id.id)
            invoice_receivables[key] = self._update_amounts(
                invoice_receivables[key],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )
        elif order.is_invoiced:
            company_id = order.account_move.company_id.id
            inter_company_receivables[company_id][key] = self._update_amounts(
                inter_company_receivables[company_id][key],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )
            inter_company_amounts[company_id] = self._update_amounts(
                inter_company_amounts[company_id],
                {"amount": order._get_amount_receivable()},
                order.date_order,
            )

    def _accumulate_amount_preprocess_data(self, data):
        def amounts():
            return {"amount": 0.0, "amount_converted": 0.0}

        old_invoice_receivables = data.get("invoice_receivables")
        invoice_receivables = defaultdict(amounts)
        inter_company_receivables = defaultdict(lambda: defaultdict(amounts))
        inter_company_amounts = defaultdict(amounts)

        data.update(
            {
                "old_invoice_receivables": old_invoice_receivables,
                "invoice_receivables": invoice_receivables,
                "inter_company_amounts": inter_company_amounts,
                "inter_company_invoice_receivables": inter_company_receivables,
            }
        )

    def _accumulate_amounts(self, data):
        result = super(
            PosSession, self.with_context(force_company=self.company_id.id)
        )._accumulate_amounts(data)
        self._accumulate_amount_preprocess_data(data)
        for order in self.order_ids:
            self._pos_session_process_order(order, data)
        inter_company_map = {}
        inter_company_move_map = {}
        for company_id in data["inter_company_amounts"]:
            inter_company = self.env["res.inter.company"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("related_company_id", "=", company_id),
                ],
                limit=1,
            )
            if not inter_company:
                raise UserError(
                    _("Intercompany relation not found between %s and %s")
                    % (
                        self.company_id.display_name,
                        self.env["res.company"]
                        .browse(company_id)
                        .display_name,
                    )
                )
            inter_company_map[company_id] = inter_company
            related_journal = inter_company.related_journal_id
            inter_company_move_map[company_id] = (
                self.env["account.move"]
                .with_context(default_journal_id=related_journal.id)
                .create(
                    {
                        "journal_id": related_journal.id,
                        "date": fields.Date.context_today(self),
                        "ref": _("Intercompany for %s") % self.name,
                        "inter_company_pos_session_id": self.id,
                    }
                )
            )

        data.update(
            {
                "inter_company_map": inter_company_map,
                "inter_company_move_map": inter_company_move_map,
            }
        )
        return result

    def _create_invoice_receivable_lines(self, data):
        result = super()._create_invoice_receivable_lines(data)
        inter_company_receivables = result["inter_company_invoice_receivables"]
        invoice_receivable_lines = data["invoice_receivable_lines"]
        MoveLine = data.get("MoveLine")
        inter_company_receivable_vals = defaultdict(lambda: defaultdict(list))
        for company, invoice_receivables in inter_company_receivables.items():
            for partner, amounts in invoice_receivables.items():
                commercial_partner = partner.commercial_partner_id
                partner_account_id = commercial_partner.with_context(
                    force_company=company
                ).property_account_receivable_id.id
                inter_company_receivable_vals[company][
                    partner_account_id
                ].append(
                    self._get_invoice_receivable_vals(
                        partner_account_id,
                        amounts["amount"],
                        amounts["amount_converted"],
                        partner=commercial_partner,
                        move=data.get("inter_company_move_map")[company],
                    )
                )
        for company, amounts in data["inter_company_amounts"].items():
            journal = data["inter_company_map"][company].journal_id
            if amounts["amount"] > 0:
                account = journal.default_credit_account_id
            else:
                account = journal.default_debit_account_id
            inter_company_receivable_vals[self.company_id.id][
                account.id
            ].append(
                self._get_invoice_receivable_vals(
                    account.id, amounts["amount"], amounts["amount_converted"],
                )
            )
        for (
            _company,
            company_receivables,
        ) in inter_company_receivable_vals.items():
            for account_id, vals in company_receivables.items():
                receivable_lines = MoveLine.create(vals)
                for receivable_line in receivable_lines:
                    if not receivable_line.reconciled:
                        key = (
                            receivable_line.partner_id.id,
                            account_id,
                        )
                        if account_id not in invoice_receivable_lines:
                            invoice_receivable_lines[key] = receivable_line
                        else:
                            invoice_receivable_lines[key] |= receivable_line
        data.update({"invoice_receivable_lines": invoice_receivable_lines})
        return data

    def _get_invoice_receivable_vals(
        self, account_id, amount, amount_converted, **kwargs
    ):
        result = super(PosSession, self)._get_invoice_receivable_vals(
            account_id, amount, amount_converted, **kwargs
        )
        move = kwargs.get("move")
        if move:
            result["move_id"] = move.id
        return result

    def _create_balancing_line(self, data):
        result = super(PosSession, self)._create_balancing_line(data)
        for move in self.inter_company_move_ids:
            imbalance_amount = 0
            for line in move.line_ids:
                # it is an excess debit so it should be credited
                imbalance_amount += line.debit - line.credit

            if not float_is_zero(
                imbalance_amount, precision_rounding=self.currency_id.rounding
            ):
                balancing_vals = self._prepare_balancing_line_vals(
                    imbalance_amount, move
                )
                related_journal = data["inter_company_map"][
                    move.company_id.id
                ].related_journal_id
                if imbalance_amount > 0:
                    account = related_journal.default_credit_account_id
                else:
                    account = related_journal.default_debit_account_id
                balancing_vals.update(
                    {
                        "account_id": account.id,
                        "name": _("Intercompany amount from %s")
                        % self.company_id.name,
                    }
                )
                MoveLine = data.get("MoveLine")
                MoveLine.create(balancing_vals)

        return result

    def _validate_session(self):
        result = super(PosSession, self)._validate_session()
        self.inter_company_move_ids.post()
        return result

    def _get_related_account_moves(self):
        result = super()._get_related_account_moves()

        def get_matched_move_lines(aml):
            if aml.credit > 0:
                return [r.debit_move_id.id for r in aml.matched_debit_ids]
            else:
                return [r.credit_move_id.id for r in aml.matched_credit_ids]

        session_move = self.inter_company_move_ids
        # get all the linked move lines to this account move.
        non_reconcilable_lines = session_move.mapped("line_ids").filtered(
            lambda aml: not aml.account_id.reconcile
        )
        reconcilable_lines = (
            session_move.mapped("line_ids") - non_reconcilable_lines
        )
        fully_reconciled_lines = reconcilable_lines.filtered(
            lambda aml: aml.full_reconcile_id
        )
        partially_reconciled_lines = (
            reconcilable_lines - fully_reconciled_lines
        )

        ids = (
            non_reconcilable_lines.ids
            + fully_reconciled_lines.mapped("full_reconcile_id")
            .mapped("reconciled_line_ids")
            .ids
            + sum(
                partially_reconciled_lines.mapped(get_matched_move_lines),
                partially_reconciled_lines.ids,
            )
        )

        return (
            self.env["account.move.line"].browse(ids).mapped("move_id")
            | result
        )
