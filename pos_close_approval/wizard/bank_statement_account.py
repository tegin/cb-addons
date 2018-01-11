# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountBankStatementLineAccount(models.TransientModel):
    _name = 'account.bank.statement.line.account'

    def _default_statement_line(self):
        active_model = self.env.context.get('active_model', False)
        if active_model:
            active_ids = self.env.context.get('active_ids', False)
            return self.env[active_model].browse(active_ids).ensure_one()
        return None

    def _default_account(self):
        return self._default_statement_line().account_id

    def _default_company(self):
        return self._default_statement_line().company_id

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True,
        default=_default_account
    )
    company_id = fields.Many2one(
        'res.company',
        default=_default_company
    )
    statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        required=True,
        default=_default_statement_line
    )

    @api.multi
    def run(self):
        for record in self:
            record.statement_line_id.write({
                'account_id': record.account_id.id
            })
        return {}
