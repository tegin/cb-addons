# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request


class AccessFastController(http.Controller):
    @http.route(
        "/access_fast/<string:action_code>/<string:code>",
        type="http",
        methods=["GET"],
        csrf=False,
    )
    def access_fast(self, action_code, code, **kwargs):

        action = request.env["ir.access.fast"].search(
            [("name", "=", action_code)], limit=1
        )
        if not action:
            return request.make_response(
                "Action not found", headers=[("Content-Type", "text/plain")], status=404
            )

        record = (
            request.env[action.model_id.model]
            .sudo()
            .search([(action.field_id.name or "name", "=", code)], limit=1)
        )
        if not record:
            return request.make_response(
                "Record not found", headers=[("Content-Type", "text/plain")], status=404
            )

        return request.redirect(f"/web#model={action.model_id.model}&id={record.id}")
