# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def button_post(self):
        lines_of_inter_moves_to_reconcile = self.line_ids.filtered(
            lambda line: line.move_id.state != "posted"
            and line.invoice_id
            and line.invoice_id.company_id != self.journal_id.company_id
        )
        result = super(AccountBankStatement, self).button_post()
        for line in lines_of_inter_moves_to_reconcile:
            move = (
                self.env["account.move"]
                .with_company(line.invoice_id.company_id.id)
                .create(self._inter_company_account_move_vals(line))
            )
            move._post()
            (line.invoice_id.line_ids | move.line_ids).filtered(
                lambda l: l.account_internal_type in ("receivable", "payable")
            ).reconcile()
        return result

    def _inter_company_account_move_vals(self, line):
        inter_company = (
            self.env["res.inter.company"]
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("related_company_id", "=", line.invoice_id.company_id.id),
                ]
            )
            .ensure_one()
        )
        return {
            "journal_id": inter_company.related_journal_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": line.invoice_id.line_ids.filtered(
                            lambda l: l.account_internal_type
                            in ("receivable", "payable")
                        ).account_id.id,
                        "debit": line.amount < 0 and -line.amount or 0.0,
                        "credit": line.amount > 0 and line.amount or 0.0,
                        "name": line.name,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": line.name,
                        "credit": line.amount < 0 and -line.amount or 0.0,
                        "debit": line.amount > 0 and line.amount or 0.0,
                        "account_id": inter_company.related_journal_id.default_account_id.id,
                    },
                ),
            ],
        }
