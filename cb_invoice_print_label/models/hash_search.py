# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import base64
from uuid import uuid4

class HashSearch(models.Model):
    _name = 'hash.search'
    _description = 'Hash Search'

    res_id = fields.Integer(required=True)
    model = fields.Char(required=True)
    name = fields.Char(required=True)

    _sql_constraints = [
        # Unique name
        # unique model, res_id
    ]

    @api.model
    def get_hash_name(self, vals):
        return base64.b64encode(
            ('%s;%s' % (vals['model'], vals['res_id'])).encode('utf-8')
        ).decode('utf-8')

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.get_hash_name(vals)
        return super().create(vals)
