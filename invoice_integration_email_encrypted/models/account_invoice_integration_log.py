# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, _
from odoo.exceptions import UserError
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO


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
                raise UserError(_('Only PDFs are allowed'))
        return result

