# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    pos_session_id = fields.Many2one(
        "pos.session",
        related="statement_id.pos_session_id",
        readonly=True,
        store=True,
    )
    pos_session_state = fields.Selection(
        related="statement_id.pos_session_id.state",
        readonly=True,
        string="Session State",
    )
    account_id = fields.Many2one(
        "account.account",
        compute="_compute_account",
        check_company=True,
    )

    @api.depends("line_ids.account_id")
    def _compute_account(self):
        for record in self:
            # We will only take the account of the line that is not liquidity.
            # If there is more than one, we will ignore it
            _liquidity, suspense, other = record._seek_for_lines()
            account = (suspense | other).mapped("account_id")
            if account and len(account) == 1:
                record.account_id = account
            else:
                record.account_id = False
