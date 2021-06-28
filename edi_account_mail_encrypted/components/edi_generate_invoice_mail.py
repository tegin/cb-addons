# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import subprocess
from io import BytesIO
from tempfile import TemporaryDirectory

from odoo import _
from odoo.addons.component.core import Component
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class EdiOutputL10nEsFacturae(Component):
    _inherit = "edi.output.generate.edi_account_mail.generate"

    def _generate(self):
        content, content_name, content_type = super()._generate()
        password = (
            self.exchange_record.record.partner_id.email_integration_password
        )
        if password:
            password = self.env["email.encryptor"]._decrypt_value(password)
            if content_type == "pdf":
                output_pdf = PdfFileWriter()
                in_buff = BytesIO(content)
                pdf = PdfFileReader(in_buff)
                output_pdf.appendPagesFromReader(pdf)
                output_pdf.encrypt(password.decode("UTF-8"))
                buff = BytesIO()
                output_pdf.write(buff)
                content = buff.getvalue()
            elif content_type != "zip":
                tmpdir = TemporaryDirectory()
                temp_filename = os.path.join(tmpdir.name, content_name)
                with open(temp_filename, "wb") as f:
                    f.write(content)
                zip_file = content_name.rsplit(".", 1)[0] + ".zip"
                process = subprocess.Popen(
                    [
                        "zip",
                        os.path.join(tmpdir.name, zip_file),
                        content_name,
                        "--password",
                        password,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir.name,
                )
                stdout, stderr = process.communicate()
                if stderr:
                    raise UserError(
                        _("The following error was raised: %s") % stderr
                    )
                content_name = zip_file
                buff = BytesIO()
                with open(os.path.join(tmpdir.name, zip_file), "rb") as f:
                    buff.write(f.read())
                content = buff.getvalue()
                content_type = "zip"
            else:
                raise UserError(
                    _("Still not implemented how to encrypt a zip file")
                )
        return content, content_name, content_type
