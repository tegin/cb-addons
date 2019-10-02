# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from odoo import api, fields, http, models
from odoo.http import request


class HttpSessionWizard(models.TransientModel):

    _name = "http.session.wizard"

    def check_session(self, session, current):
        return session.db == current.db and session.uid

    def get_sessions(self):
        store = http.root.session_store
        mvals = []
        current = request.session
        for sid in store.list():
            session = store.get(sid)
            if self.check_session(session, current):
                mvals.append(
                    {
                        "user_id": session.uid,
                        "ctx": session.ctx,
                        "geoip": session.geoip,
                        "current_session": session.sid == current.sid,
                        "session_token": session.session_token,
                        "session_id": sid,
                        "update_time": fields.Datetime.to_string(
                            datetime.fromtimestamp(session.update_time)
                        ),
                    }
                )
        result = self.env["http.session.user"]
        for vals in mvals:
            result |= self.env["http.session.user"].create(vals)
        return result

    @api.multi
    def doit(self):
        sessions = self.get_sessions()
        action = self.env.ref(
            "web_session_management.http_session_user_act_window"
        )
        result = action.read()[0]
        result["domain"] = [("id", "in", sessions.ids)]
        return result

    @api.model
    def clean_sessions(self):
        store = http.root.session_store
        for sid in store.list():
            session = store.get(sid)
            if session.uid:
                date = session.update_time or 0
                delay = self.env[
                    "res.users"
                ]._auth_timeout_deadline_calculate()
                if delay and date < delay:
                    session.logout()
                    store.save(session)
            if (
                self.env.context.get("clean_unlogged", False)
                and not session.uid
            ):
                store.delete(session)
