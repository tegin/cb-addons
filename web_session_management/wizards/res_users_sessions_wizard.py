# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
import os
from odoo import api, fields, models, http
from odoo.http import request
from werkzeug.contrib.sessions import FilesystemSessionStore


class ResUsersSessionsWizard(models.TransientModel):
    _name = 'res.users.sessions.wizard'

    user_ids = fields.Many2many(
        'res.users',
        default=lambda r: [(4, r.env.uid)]
    )

    def check_session(self, session, current):
        return (
            session.db == current.db and
            session.uid and
            session.uid in self.user_ids.ids
        )

    def get_sessions(self):
        store = http.root.session_store
        mvals = []
        current = request.session
        for sid in store.list():
            session = store.get(sid)
            if self.check_session(session, current):
                mvals.append({
                    'user_id': session.uid,
                    'ctx': session.ctx,
                    'geoip': session.geoip,
                    'current_session': session.sid == current.sid,
                    'session_token': session.session_token,
                    'session_id': sid,
                    'date': self.get_store_date(store, session)
                })
        result = self.env['http.session.user']
        for vals in mvals:
            result |= self.env['http.session.user'].create(vals)
        return result

    @api.model
    def get_store_date(self, store, session):
        if isinstance(store, FilesystemSessionStore):
            return datetime.fromtimestamp(os.path.getmtime(
                store.get_session_filename(session.sid)))
        return False

    @api.multi
    def doit(self):
        sessions = self.get_sessions()
        action = self.env.ref(
            'web_session_management.http_session_user_act_window')
        result = action.read()[0]
        result['domain'] = [('id', 'in', sessions.ids)]
        return result
