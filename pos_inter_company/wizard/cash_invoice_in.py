# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CashInvoiceIn(models.TransientModel):
    _inherit = "cash.invoice.in"

    inter_company_ids = fields.Many2many(
        "res.company", related="company_id.related_company_ids", readonly=True
    )

    def _calculate_values_for_statement_line(self, record):
        res = super()._calculate_values_for_statement_line(record)
        if self.invoice_id and self.invoice_id.company_id != self.journal_id.company_id:
            account = self.invoice_id.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ("receivable", "payable")
            )
            inter_company = (
                self.env["res.inter.company"]
                .search(
                    [
                        ("company_id", "=", self.journal_id.company_id.id),
                        ("related_company_id", "=", account.company_id.id),
                    ]
                )
                .ensure_one()
            )
            res.update(
                {
                    "counterpart_account_id": inter_company.journal_id.default_account_id.id
                }
            )
        return res
