# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResUsersSessionsWizard(models.TransientModel):
    _name = "res.users.sessions.wizard"
    _inherit = "http.session.wizard"

    user_ids = fields.Many2many(
        "res.users", default=lambda r: [(4, r.env.uid)]
    )

    def check_session(self, session, current):
        return (
            super().check_session(session, current)
            and session.uid in self.user_ids.ids
        )
