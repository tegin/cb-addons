# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64

from odoo import models


class AccountInvoiceIntegrationMethod(models.Model):
    _inherit = "account.invoice.integration.method"

    def integration_values(self, invoice):
        res = super().integration_values(invoice)
        if self == self.env.ref(
            "l10n_es_facturae_storage.integration_storage"
        ):
            res.update(self._storage_integration_values(invoice))
        return res

    def _get_storage_integration_action(self, invoice):
        return invoice.partner_id.account_integration_report_id

    def _storage_integration_values(self, invoice):
        action = self._get_storage_integration_action(invoice)
        content, content_type = action.render(invoice.ids)
        attachment = False
        if action.attachment:
            attachment = action.retrieve_attachment(invoice)
        if not attachment:
            fname = invoice.partner_id.account_integration_filename_pattern
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
