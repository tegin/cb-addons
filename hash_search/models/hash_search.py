# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from ast import literal_eval
import base64
import json


class HashSearch(models.Model):
    _name = 'hash.search'
    _description = 'Hash Search'

    res_id = fields.Integer(required=True)
    model = fields.Char(required=True)
    name = fields.Char(required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'name must be unique'),
        ('res_id_model_unique', 'unique(res_id, model)',
         'res_id and model must be unique'),
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

    @api.multi
    def find_hash(self, barcode):
        hash = self.search([('name', '=', barcode)], limit=1)
        if not hash:
            action = self.env.ref('hash_search.find_hash')
            result = action.read()[0]
            context = literal_eval(result['context'])
            context.update({
                'default_state': 'warning',
                'default_status': _('Hash %s cannot be found') % barcode
            })
            result['context'] = json.dumps(context)
            return result
        res = self.env[hash.model].browse(hash.res_id)
        # TODO: Check that the user can access the element
        result = {
            "type": "ir.actions.act_window",
            "res_model": hash.model,
            "views": [[res.get_formview_id(), "form"]],
            "res_id": hash.res_id,
            "target": "main",
        }
        return result
