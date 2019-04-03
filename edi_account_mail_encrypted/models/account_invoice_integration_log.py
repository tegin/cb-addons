# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
from tempfile import TemporaryDirectory
import logging
from io import BytesIO
import subprocess
import os
_logger = logging.getLogger(__name__)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class AccountInvoiceIntegrationLog(models.Model):
    _name = 'account.invoice.integration.log'
    _inherit = ['account.invoice.integration.log', 'email.encryptor']

    def get_email_attachments(self, invoice):
        res = super().get_email_attachments(invoice)
        if not self.integration_id.email_password:
            return res
        result = []
        password = self._decrypt_value(
            self.integration_id.email_password)
        zip_file = False
        tmpdir = TemporaryDirectory()
        for name, content, mime in res:
            if mime == 'application/pdf':
                output_pdf = PdfFileWriter()
                in_buff = BytesIO(content)
                pdf = PdfFileReader(in_buff)
                output_pdf.appendPagesFromReader(pdf)
                output_pdf.encrypt(password.decode('UTF-8'))
                buff = BytesIO()
                output_pdf.write(buff)
                result.append((name, buff.getvalue(), mime))
            else:
                if not zip_file:
                    zip_file = invoice.number + '.zip'
                with open(os.path.join(tmpdir.name, name), 'wb') as f:
                    f.write(content)
                process = subprocess.Popen(
                    [
                        "zip", zip_file, name, "--password", password
                    ],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    cwd=tmpdir.name
                )
                process.communicate()
        if zip_file:
            buff = BytesIO()
            with open(os.path.join(tmpdir.name, zip_file), 'rb') as f:
                buff.write(f.readall())
            result.append((zip_file, buff.getvalue(), 'application/zip'))
        return result
