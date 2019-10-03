# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MedicalPatient(models.Model):

    _inherit = 'medical.patient'

    @api.multi
    def assign_surgical_appointment(self, context=False):
        self.ensure_one()
        appointment_id = context.get(
            'active_id', False
        )
        appointment = self.env['medical.surgical.appointment'].browse(
            appointment_id
        )
        appointment.patient_id = self
        return appointment.with_context(
            generate_from_wizard=True
        ).generate_encounter()
