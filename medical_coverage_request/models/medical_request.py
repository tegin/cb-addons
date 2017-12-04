
from odoo import models, fields


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    coverage_id = fields.Many2one(
        'medical.coverage',
        required=True,
        domain="[('patient_id', '=', patient_id)]"
    )
