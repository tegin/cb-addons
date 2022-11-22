# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.addons.component.core import Component


class EdiOutputL10nEsFacturae(Component):
    _name = "edi.output.generate.edi_account_mail.generate"
    _inherit = "edi.component.output.mixin"
    _usage = "output.generate"
    _backend_type = "account_move_mail"

    def generate(self):
        datas, filename, filetype = self._generate()
        self.exchange_record.write({"exchange_filename": filename})
        return datas

    def get_email_integration_action(self):
        return (
            self.exchange_record.record.partner_id.invoice_report_email_id
            or self.env.ref("account.account_invoices")
        )

    def _generate(self):
        action = self.get_email_integration_action()
        content, content_type = action._render(self.exchange_record.record.ids)
        filename = self.exchange_record.exchange_filename.rsplit(".")[0]
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        return self._post_generate(
            content, "{}.{}".format(filename, content_type), content_type
        )

    def _post_generate(self, content, content_name, content_type):
        """Hook used if we want to generate zip files or add attachments"""
        return content, content_name, content_type
