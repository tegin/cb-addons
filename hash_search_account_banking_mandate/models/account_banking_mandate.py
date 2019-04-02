# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountBankingMandate(models.Model):
    _name = 'account.banking.mandate'
    _inherit = ['account.banking.mandate', 'hash.search.mixin']

    @api.model
    def _get_hash_button(self):
        button = super()._get_hash_button()
        button.attrib['invisible'] = "1"
        return button
