# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def recompute_lines_agents(self):
        # Commission on medical sale orders will not be managed by the
        # recompute function
        return super(
            AccountInvoice, self.filtered(lambda r: not r.is_medical)
        ).recompute_lines_agents()


class AccountInvoiceLineAgent(models.Model):
    _inherit = 'account.invoice.line.agent'

    procedure_id = fields.Many2one(
        'medical.procedure',
        readonly=True,
    )
    laboratory_event_id = fields.Many2one(
        'medical.laboratory.event',
        string='Laboratory Event',
    )

    @api.model_cr_context
    def _auto_init(self):
        constraints = []
        for (key, definition, message) in self._sql_constraints:
            if key == 'unique_agent':
                constraints.append((
                    'unique_agent_procedure',
                    'UNIQUE(invoice_line, agent, parent_agent_line_id, '
                    'procedure_id, is_cancel)',
                    'You can only add one time each agent.'
                ))
            else:
                constraints.append((key, definition, message))
        self._sql_constraints = constraints
        res = super()._auto_init()
        self._add_sql_constraints()
        return res

    def get_commission_cancel_vals(self, agent=False):
        res = super().get_commission_cancel_vals(agent)
        res['procedure_id'] = self.procedure_id.id or False
        return res
