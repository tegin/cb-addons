from odoo import api, fields, models


class AccountInvoiceAgentChange(models.TransientModel):
    _name = 'account.invoice.agent.change'

    agent = fields.Many2one(
        'res.partner',
        domain=[('agent', '=', True)],
        required=True
    )
    agent_line = fields.Many2one(
        'account.invoice.line.agent',
        required=True,
        readonly=True
    )

    @api.multi
    def run(self):
        self.ensure_one()
        self.agent_line.change_agent(self.agent)
        return {'type': 'ir.actions.client', 'tag': 'reload'}
