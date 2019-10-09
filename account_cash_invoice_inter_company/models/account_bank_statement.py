# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    inter_company_statement_id = fields.Many2one(
        "account.bank.statement", "Initial statement"
    )

    inter_company_statement_ids = fields.One2many(
        "account.bank.statement", "inter_company_statement_id"
    )

    @api.multi
    def button_confirm_bank(self):
        res = super(
            AccountBankStatement,
            self.with_context(force_company=self.company_id.id),
        ).button_confirm_bank()
        for statement in self:
            for inverse in statement.inter_company_statement_ids:
                inverse.balance_end_real = inverse.balance_end
                inverse.with_context(
                    force_company=inverse.company_id.id
                ).button_confirm_bank()
        return res

    @api.multi
    def check_confirm_bank(self):
        return super(
            AccountBankStatement,
            self.with_context(force_company=self.company_id.id),
        ).check_confirm_bank()
