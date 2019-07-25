# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountInvoiceIntegrationMethod(models.Model):
    _name = 'account.invoice.integration.method'
    _inherit = ['account.invoice.integration.method', 'email.encryptor']

    def email_integration_values(self, invoice):
        res = super().email_integration_values(invoice)
        if invoice.partner_id.email_integration_password:
            password = self._decrypt_value(
                invoice.partner_id.email_integration_password)
            value = self.env['mail.template']._render_template(
                password, invoice._name, invoice.id
            )
            res['email_password'] = self._encrypt_value(value)
        return res
