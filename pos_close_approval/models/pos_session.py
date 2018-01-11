# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    state = fields.Selection(
        selection_add=[('pending_approval', 'Pending approval')]
    )

    @api.constrains('config_id')
    def _check_pos_config(self):
        if not self.config_id.requires_approval:
            return super(PosSession, self)._check_pos_config()
        if self.search_count(
                [('state', 'not in', ['closed', 'pending_approval']),
                 ('config_id', '=', self.config_id.id)]) > 1:
            raise ValidationError(_("You cannot create two active sessions "
                                    "related to the same point of sale"))

    @api.multi
    def action_pos_session_approve(self):
        for session in self:
            for statement in session.statement_ids:
                statement.write({'balance_end_real': statement.balance_end})
            session.action_pos_session_close()

    @api.multi
    def action_pos_session_closing_control(self):
        approved = 0
        for record in self:
            if not record.config_id.requires_approval:
                approved += 1
        if approved == len(self):
            return super(PosSession, self).action_pos_session_closing_control()
        if approved == 0:
            self.write({
                'state': 'pending_approval',
                'stop_at': fields.Datetime.now()
            })
            return
        raise UserError(_('Cannot close different kinds of sessions'))
