from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    parent_agent_line_id = fields.Many2one(
        'account.invoice.line.agent',
        readonly=True,
    )
    child_agent_line_ids = fields.One2many(
        'account.invoice.line.agent',
        inverse_name='parent_agent_line_id',
        readonly=True,
    )
    is_cancel = fields.Boolean(default=False, required=True, readonly=True)
    can_cancel = fields.Boolean(
        compute='_compute_can_cancel', store=True,
    )

    @classmethod
    def _build_model_attributes(cls, pool):
        res = super()._build_model_attributes(pool)
        constraints = []
        for (key, definition, message) in cls._sql_constraints:
            if key in ['unique_agent']:
                constraints.append((
                    key,
                    'UNIQUE(object_id, agent, parent_agent_line_id, '
                    'is_cancel)',
                    message
                ))
            else:
                constraints.append((key, definition, message))
        cls._sql_constraints = constraints
        return res

    @api.depends('child_agent_line_ids', 'is_cancel',
                 'object_id.invoice_id.state')
    def _compute_can_cancel(self):
        for rec in self:
            rec.can_cancel = (
                not rec.child_agent_line_ids and
                not rec.is_cancel and
                rec.object_id.invoice_id.state != 'draft'
            )

    @api.constrains('parent_agent_line_id', 'is_cancel')
    def _check_cancel(self):
        for record in self:
            if record.is_cancel and not record.parent_agent_line_id:
                raise ValidationError(_('Cancelled lines must have a parent.'))

    @api.depends('object_id.price_subtotal', 'is_cancel',
                 'parent_agent_line_id.amount')
    def _compute_amount(self):
        res = super(AccountInvoiceLineAgent, self.filtered(
            lambda r: not r.is_cancel))._compute_amount()
        for record in self.filtered(lambda r: r.is_cancel):
            record.amount = - record.parent_agent_line_id.amount
        return res

    def get_commission_cancel_vals(self, agent=False):
        return {
            'parent_agent_line_id': self.id,
            'object_id': self.object_id.id,
            'commission': self.commission.id,
            'agent_line': False,
            'agent': agent.id if agent else self.agent.id,
            'is_cancel': self.is_cancel if agent else not self.is_cancel,
        }

    def change_agent(self, agent):
        self.ensure_one()
        if agent == self.agent:
            return
        if not self.agent_line:
            self.agent = agent
            return
        self.create(self.get_commission_cancel_vals())
        self.create(self.get_commission_cancel_vals(agent))
