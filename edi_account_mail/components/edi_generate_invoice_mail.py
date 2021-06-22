# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EdiOutputL10nEsFacturae(Component):
    _name = "edi.output.generate.l10n_es_facturae"
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
        content, content_type = action.render(self.exchange_record.record.ids)
        return content, "Invoice.%s" % content_type, content_type
