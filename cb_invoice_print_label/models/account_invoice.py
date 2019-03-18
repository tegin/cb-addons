from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _get_hash_button_attrs(self):
        return {
            "invisible": [("type", "in", ["out_invoice", "out_refund"])]
        }
