import werkzeug
from odoo import http
from odoo.http import request
from werkzeug import url_encode


class FormController(http.Controller):
    @http.route("/form/fill_form", auth="user")
    def fill_form(self, template_id=None):
        form_action = request.env["custom.info.form"]._generate_form(
            int(template_id)
        )
        url_params = {
            "view_type": form_action["view_type"],
            "model": form_action["res_model"],
            "id": form_action["res_id"],
            "active_id": form_action["res_id"],
            "action": form_action.get("id"),
        }
        url = "/web?#%s" % url_encode(url_params)
        return werkzeug.utils.redirect(url)
