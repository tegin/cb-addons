# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def closed_states(self):
        return ["closed"]

    @api.depends("session_ids", "session_ids.state")
    def _compute_current_session(self):
        for pos_config in self:
            opened_sessions = pos_config.session_ids.filtered(
                lambda r: r.state not in self.closed_states()
            )
            pos_config.number_of_opened_session = len(opened_sessions)
            pos_config.has_active_session = opened_sessions and True or False
            pos_config.current_session_id = opened_sessions
            pos_config.current_session_state = opened_sessions.state

    def open_ui(self):
        self.ensure_one()
        return self._open_session(self.current_session_id.id)
