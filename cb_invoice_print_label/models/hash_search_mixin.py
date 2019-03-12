# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HashSearchMixin(models.AbstractModel):
    _name = 'hash.search.mixin'

    hash_search_ids = fields.One2many(
        'hash.search',
        compute='_compute_hash_search'
    )

    @api.depends()
    def _compute_hash_search(self):
        for record in self:
            record.hash_search_ids = record.get_hash_search()

    def _hash_values(self):
        return {
            'res_id': self.id,
            'model': self._name,
        }

    @api.multi
    def get_hash_search(self):
        self.ensure_one()
        hash = self.env['hash.search'].search([
            ('res_id', '=', self.id),
            ('model', '=', self._name),
        ], limit=1)
        if not hash:
            return self.env['hash.search'].create(self._hash_values())
        return hash
