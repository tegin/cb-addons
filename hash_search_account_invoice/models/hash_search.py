# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HashSearch(models.Model):
    _inherit = 'hash.search'

    @api.model
    def hash_search_models(self):
        res = super().hash_search_models()
        res.append(('account.invoice', 'Invoice'))
        return res
