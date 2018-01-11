# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    pos_session_id = fields.Many2one(
        'pos.session',
        related='statement_id.pos_session_id'
    )
    pos_session_state = fields.Selection(
        related='statement_id.pos_session_id.state'
    )
