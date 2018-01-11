# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def closed_states(self):
        return ['closed']

    @api.depends('session_ids')
    def _compute_current_session(self):
        for pos_config in self:
            session = pos_config.session_ids.filtered(
                lambda r: r.state not in self.closed_states()
            )
            pos_config.current_session_id = session
            pos_config.current_session_state = session.state

    @api.multi
    def open_ui(self):
        self.ensure_one()
        return self._open_session(self.current_session_id.id)
