# Copyright 2017-21 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class BankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    account_id = fields.Many2one(check_company=False)

    def inter_company_payment(self):
        self.ensure_one()
        inter_company = (
            self.env["res.inter.company"]
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("related_company_id", "=", self.account_id.company_id.id),
                ]
            )
            .ensure_one()
        )
        journal = inter_company.journal_id
        related_journal = inter_company.related_journal_id
        account = journal.default_account_id
        vals = {
            "name": self.name,
            "debit": self.amount < 0 and -self.amount or 0.0,
            "credit": self.amount > 0 and self.amount or 0.0,
            "account_id": account.id,
        }
        self.process_reconciliation(new_aml_dicts=[vals])
        statement = self.statement_id
        inverse_statement = statement.inter_company_statement_ids.filtered(
            lambda r: r.journal_id.id == related_journal.id
        )
        if not inverse_statement:
            inverse_statement = self.env["account.bank.statement"].create(
                {
                    "name": statement.name,
                    "journal_id": related_journal.id,
                    "inter_company_statement_id": statement.id,
                }
            )
        self.copy({"statement_id": inverse_statement.id})

    def fast_counterpart_creation(self):
        for st_line in self:
            company = st_line.statement_id.company_id
            if st_line.account_id and st_line.account_id.company_id.id != company.id:
                st_line.with_company(st_line.statement_id.company_id.id).with_context(
                    journal_id=st_line.statement_id.journal_id.id,
                    default_journal_id=st_line.statement_id.journal_id.id,
                ).inter_company_payment()
            else:
                super(
                    BankStatementLine,
                    st_line.with_company(
                        st_line.statement_id.company_id.id
                    ).with_context(
                        journal_id=st_line.statement_id.journal_id.id,
                        default_journal_id=st_line.statement_id.journal_id.id,
                    ),
                ).fast_counterpart_creation()

    @api.constrains("company_id", "account_id")
    def _check_company_id_account_id(self):
        return
