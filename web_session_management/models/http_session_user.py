# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _, http
from odoo.exceptions import UserError


class HttpSessionUser(models.TransientModel):
    _name = 'http.session.user'
    _description = 'User sessions'

    user_id = fields.Many2one('res.users', readonly=True)
    current_session = fields.Boolean(readonly=True)
    session_id = fields.Char(readonly=True)
    session_token = fields.Char(readonly=True)
    date = fields.Datetime()
    ctx = fields.Serialized(readonly=True)
    geoip = fields.Serialized(readonly=True)

    @api.multi
    def kill(self):
        self.ensure_one()
        if self.current_session:
            raise UserError(_('Current session cannot be killed'))
        store = http.root.session_store
        session = store.get(self.session_id)
        session.logout(keep_db=True)
        store.save(session)
        self.unlink()
