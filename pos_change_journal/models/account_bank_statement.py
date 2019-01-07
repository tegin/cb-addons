from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    pos_session_id = fields.Many2one(
        'pos.session',
        related='statement_id.pos_session_id',
        readonly=True
    )
