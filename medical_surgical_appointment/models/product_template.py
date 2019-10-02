# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    allow_surgical_appointment = fields.Boolean(
        string='Allow Surgical Appointment',
    )

    surgical_appointment_time = fields.Float()

    anesthesia_type = fields.Selection(
        [
            ('no', 'No Anesthesia'),
            ('sedation', 'Sedation')
        ], default=False
    )

    patient_interned = fields.Boolean(string='Patient Interned')
