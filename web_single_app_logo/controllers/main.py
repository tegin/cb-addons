# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import functools
import imghdr
import io

from odoo import http
from odoo.modules import get_resource_path


class MulticompanyLogo(http.Controller):
    @http.route(["/app_logo.png"], type="http", auth="none", cors="*")
    def app_logo(self):
        imgname = "logo"
        imgext = ".png"
        request = http.request
        placeholder = functools.partial(
            get_resource_path, "web", "static", "src", "img"
        )
        if not request.env:
            return http.Stream(placeholder(imgname + imgext))
        try:
            key = "app.logo"
            image = (
                request.env["ir.config_parameter"]
                .sudo()
                .search_read(
                    [("key", "=", key)],
                    fields=["value", "write_date"],
                    limit=1,
                )
            )
            if image:
                image_base64 = base64.b64decode(image[0]["value"])
                image_data = io.BytesIO(image_base64)
                imgext = "." + (imghdr.what(None, h=image_base64) or "png")
                response = http.Stream(
                    type="data",
                    data=image_data.getvalue(),
                    filename=imgname + imgext,
                    mimetype=image[0]["write_date"],
                )
            else:
                response = http.Stream(data=placeholder("nologo.png")).get_response()
        except Exception:
            response = http.Stream(data=placeholder(imgname + imgext)).get_response()
        return response.get_response()
