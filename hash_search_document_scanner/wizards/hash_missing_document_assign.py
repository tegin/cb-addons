# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HashMissingDocumentAssign(models.TransientModel):
    _name = 'hash.missing.document.assign'

    object_id = fields.Reference(
        selection=lambda r: r.env['hash.search'].hash_search_models(),
        required=True,
    )
    missing_document_id = fields.Many2one(
        'hash.missing.document',
        required=True,
    )

    @api.multi
    def doit(self):
        self.ensure_one()
        self.missing_document_id.assign_model(
            self.object_id._name, self.object_id.id)
        return True

    @api.onchange('object_id')
    def _onchange_object_set_domain(self):
        return {'domain': {'object_id': []}}
