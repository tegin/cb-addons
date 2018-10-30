from odoo import api, fields, models


class AccountBankStatementLineChangeJournal(models.TransientModel):
    _name = 'account.bank.statement.line.change.journal'

    @api.model
    def _default_journal(self):
        session = self.env['pos.session'].browse(
            self.env.context.get('default_session_id')
        )
        return session.statement_ids.mapped('journal_id')

    line_id = fields.Many2one(
        'account.bank.statement.line',
        required=True,
        readonly=True,
    )
    journal_id = fields.Many2one(
        'account.journal',
        required=True,
        domain="[('id', 'in', journal_ids)]"
    )
    journal_ids = fields.Many2many(
        'account.journal',
        required=True,
        readonly=True,
        default=_default_journal
    )
    session_id = fields.Many2one(
        'pos.session',
        required=True,
        readonly=True,
    )

    @api.multi
    def run(self):
        self.ensure_one()
        self.line_id.write({
            'statement_id': self.session_id.statement_ids.filtered(
                lambda r: r.journal_id == self.journal_id
            ).id
        })
