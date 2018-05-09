from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    third_party_sequence_id = fields.Many2one(
        'ir.sequence',
    )
