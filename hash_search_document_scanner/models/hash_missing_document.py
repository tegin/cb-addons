# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HashMissingDocument(models.Model):
    _name = 'hash.missing.document'
    _description = 'Missing Document'  # TODO

    name = fields.Char(required=True, readonly=True)
    data = fields.Binary(attachment=True, required=True, readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('deleted', 'Deleted')
    ], default='pending')
    hash_search_id = fields.Many2one(
        'hash.search',
        readonly=True
    )

    @api.multi
    def assign_model(self, model, res_id):
        res = self.env[model].browse(res_id)
        res.ensure_one()
        hsh = res.get_hash_search()
        self.assign_hash(hsh)

    def _processed_values(self, hsh):
        return {
            'state': 'processed',
            'hash_search_id': hsh.id,
        }

    def _deleted_values(self):
        return {
            'state': 'deleted'
        }

    @api.multi
    def assign_hash(self, hsh):
        records = self.filtered(lambda r: r.state == 'pending')
        for record in records:
            hsh._attach_document(record.name, record.data)
        records.write(self._processed_values(hsh))

    @api.multi
    def delete_missing_image(self):
        self.filtered(lambda r: r.state == 'pending').write(
            self._deleted_values()
        )
