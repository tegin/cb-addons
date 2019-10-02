# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from odoo import models, _


class AccountInvoiceIntegrationMethod(models.Model):
    _inherit = "account.invoice.integration.method"

    def integration_values(self, invoice):
        res = super().integration_values(invoice)
        if self == self.env.ref("l10n_es_facturae_sftp.integration_sftp"):
            res.update(self.sftp_integration_values(invoice))
        return res

    def get_sftp_integration_action(self, invoice):
        return invoice.partner_id.ssh_report_id

    def sftp_integration_values(self, invoice):
        action = self.get_sftp_integration_action(invoice)
        content, content_type = action.render(invoice.ids)
        attachment = False
        if action.attachment:
            attachment = action.retrieve_attachment(invoice)
        if not attachment:
            fname = _("Invoice %s") % invoice.number
            attachment = self.env["ir.attachment"].create(
                {
                    "name": fname,
                    "datas": base64.b64encode(content),
                    "datas_fname": fname,
                    "res_model": "account.invoice",
                    "res_id": invoice.id,
                    "mimetype": "application/pdf",
                }
            )
        return {"attachment_id": attachment.id}
