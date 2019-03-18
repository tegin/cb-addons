# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'hash.search.mixin']

    @api.model
    def _get_label_action(self):
        return self.env.ref(
            'hash_search_account_invoice.account_invoice_hash_print_label')
