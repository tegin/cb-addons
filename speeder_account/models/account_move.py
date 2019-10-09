from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    narration = fields.Text(readonly=True)
    ref = fields.Char(readonly=True)
    statement_id = fields.Many2one(readonly=True)
    journal_id = fields.Many2one(readonly=True)
    company_id = fields.Many2one(readonly=True)
    date = fields.Date(readonly=True)
    user_type_id = fields.Many2one(readonly=True)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    company_id = fields.Many2one(readonly=True)
    company_currency_id = fields.Many2one(readonly=True)
