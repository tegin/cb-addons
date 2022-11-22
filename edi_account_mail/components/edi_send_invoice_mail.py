# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import mimetypes
from email.utils import formataddr

from odoo import tools

from odoo.addons.component.core import Component


class EdiOutputAccountMoveSendMail(Component):
    _name = "edi.output.send.edi_account_mail.send"
    _usage = "output.send"
    _backend_type = "account_move_mail"
    _inherit = "edi.component.send.mixin"

    def _get_extra_attachment(self):
        return []

    def _get_email_template(self):
        return self.env.ref("account.email_template_edi_invoice")

    def _get_email(self, partner, key):
        if partner.email_integration:
            mails = partner.email_integration.split(",")
        else:
            mails = [partner.email or "False"]
        return [formataddr((partner.name or "False", mail)) for mail in mails]

    def get_email_attachments(self):
        result = [
            (
                self.exchange_record.exchange_filename,
                base64.b64decode(self.exchange_record.exchange_file),
                mimetypes.guess_type(self.exchange_record.exchange_filename)[0],
            )
        ]
        result += self._get_extra_attachment()
        return result

    def send(self):
        IrMailServer = self.env["ir.mail_server"]
        attachments = self.get_email_attachments()
        record = self.exchange_record.record
        values = (
            self._get_email_template()
            .with_context(no_website_action=True)
            .generate_email(record.ids, ["subject", "body_html"])[record.id]
        )
        msg = IrMailServer.build_email(
            email_from=self._get_email(record.company_id.partner_id, "mail_from")[0],
            email_to=self._get_email(record.partner_id, "mail_to"),
            subject=values["subject"],
            body=values["body"],
            body_alternative=tools.html2plaintext(values["body"]),
            email_cc=[],
            attachments=attachments,
            # references=self._get_email_references(),
            object_id="{}-{}".format(record.id, record._name),
            subtype="html",
            subtype_alternative="plain",
            # headers=self._get_email_headers()
        )
        IrMailServer.send_email(msg)
