# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os
from datetime import datetime
from werkzeug.contrib.sessions import FilesystemSessionStore
from odoo import api, fields, http, models
from odoo.http import request


class HttpSessionWizard(models.TransientModel):

    _name = 'http.session.wizard'

    def check_session(self, session, current):
        return (
            session.db == current.db and
            session.uid
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
                    'update_time': fields.Datetime.to_string(
                        datetime.fromtimestamp(session.update_time)),
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

    @api.model
    def clean_sessions(self):

        store = http.root.session_store
        for sid in store.list():
            session = store.get(sid)
            if not session.uid:
                date = self.get_store_date(store, session)
