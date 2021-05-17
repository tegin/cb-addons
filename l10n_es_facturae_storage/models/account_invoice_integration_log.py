# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import re
import traceback
from io import BytesIO, StringIO

from odoo import models

_logger = logging.getLogger(__name__)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class AccountInvoiceIntegrationLog(models.Model):
    _inherit = "account.invoice.integration.log"

    def send_method(self):
        if self.integration_id.method_id == self.env.ref(
            "l10n_es_facturae_storage.integration_storage"
        ):
            return self._send_storage()
        return super().send_method()

    def _send_storage(self):
        try:
            output_pdf = PdfFileWriter()
            content = self.integration_id.attachment_id.datas
            in_buff = BytesIO(base64.b64decode(content))
            pdf = PdfFileReader(in_buff)
            output_pdf.appendPagesFromReader(pdf)
            for attachment in self.integration_id.attachment_ids:
                content = attachment.datas
                in_buff = BytesIO(base64.b64decode(content))
                pdf = PdfFileReader(in_buff)
                output_pdf.appendPagesFromReader(pdf)
            buff = BytesIO()
            output_pdf.write(buff)
            final_data = buff.getvalue()
            partner = self.integration_id.invoice_id.partner_id
            # We need to clean the filename, as we cannot send special characters
            filename = re.sub(
                r"[\\\/]",
                "",
                partner.account_integration_filename_pattern.format(
                    integration=self.integration_id,
                    invoice=self.integration_id.invoice_id,
                ),
            )
            partner.account_integration_storage_id._add_bin_data(
                filename, final_data
            )
        except Exception as error:
            buff = StringIO()
            traceback.print_exc(file=buff)
            _logger.error(buff.getvalue())
            self.state = "failed"
            self.integration_id.state = "failed"
            self.log = error
            return
        self.state = "sent"
        self.integration_id.state = "sent"
        self.integration_id.can_send = False
        self.integration_id.can_cancel = False
        self.integration_id.can_update = False
