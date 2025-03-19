# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import functools
import io

from odoo import http
from odoo.modules import get_resource_path
from odoo.tools.mimetypes import guess_mimetype


class MulticompanyLogo(http.Controller):
    @http.route(["/app_logo.png"], type="http", auth="none", cors="*")
    def app_logo(self):
        imgname = "logo"
        imgext = ".png"
        request = http.request
        placeholder = functools.partial(get_resource_path, "web", "static", "img")
        if not request.env:
            return http.Stream(
                type="path",
                path=placeholder(imgname + imgext),
                download_name=imgname + imgext,
            )
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
                mimetype = guess_mimetype(image_base64, default="image/png")
                imgext = "." + mimetype.split("/")[1]
                if imgext == ".svg+xml":
                    imgext = ".svg"
                response = http.Stream(
                    type="data",
                    data=image_data.getvalue(),
                    download_name=imgname + imgext,
                    last_modified=image[0]["write_date"],
                )
            else:
                response = http.Stream(
                    type="path",
                    path=placeholder("nologo.png"),
                    download_name="nologo.png",
                )
        except Exception:
            response = http.Stream(
                type="path",
                path=placeholder(imgname + imgext),
                download_name=imgname + imgext,
            )
        return response.get_response()
