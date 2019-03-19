# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'hash.search.mixin']

    @api.model
    def _get_label_action(self):
        return self.env.ref(
            'hash_search_account_purchase.purchase_order_hash_print_label')
