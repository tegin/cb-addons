# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from email.utils import formataddr
from odoo import models, tools
import logging
import traceback
from io import StringIO
_logger = logging.getLogger(__name__)


class AccountInvoiceIntegrationLog(models.Model):
    _inherit = 'account.invoice.integration.log'

    def send_method(self):
        if self.integration_id.method_id == self.env.ref(
            'invoice_integration_email.integration_email'
        ):
            return self.send_email()
        return super().send_method()

    def get_email_attachments(self, invoice):
        result = []
        if self.integration_id.attachment_id:
            attach = self.integration_id.attachment_id.sudo().read(
                ['datas_fname', 'datas', 'mimetype'])[0]
            result += [(
                attach['datas_fname'],
                base64.b64decode(attach['datas']), attach['mimetype'])]
        result += [(
            a['datas_fname'],
            base64.b64decode(a['datas']), a['mimetype']
        )for a in self.integration_id.attachment_ids.sudo().read(
            ['datas_fname', 'datas', 'mimetype'])]
        return result

    def send_email(self):
        try:
            invoice = self.integration_id.invoice_id
            attachments = self.get_email_attachments(invoice)
            IrMailServer = self.env['ir.mail_server']
            values = self._get_email_template().with_context(
                no_website_action=True
            ).generate_email(
                invoice.ids, ['subject', 'body_html'])[invoice.id]
            msg = IrMailServer.build_email(
                email_from=self._get_email(
                    invoice.company_id.partner_id)[0],
                email_to=self._get_email(invoice.partner_id),
                subject=values['subject'],
                body=values['body'],
                body_alternative=tools.html2plaintext(values['body']),
                email_cc=[],
                attachments=attachments,
                # references=self._get_email_references(),
                object_id='%s-%s' % (self.id, self._name),
                subtype='html',
                subtype_alternative='plain',
                # headers=self._get_email_headers()
            )
            IrMailServer.send_email(msg)
            self.write({
                'state': 'sent'
            })
            self.integration_id.write({
                'state': 'sent',
                'can_send': False,
            })
        except Exception:
            buff = StringIO()
            traceback.print_exc(file=buff)
            _logger.error(buff.getvalue())
            self.state = 'failed'
            self.integration_id.write({
                'state': 'failed'
            })

    def _get_email_template(self):
        return self.env.ref(
            'account.email_template_edi_invoice')

    def _get_email_from(self):
        return self.invoice_id.company_id.email

    def _get_email(self, partner):
        return [formataddr(
                (partner.name or 'False', partner.email or 'False'))]
