# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalSurgicalAppointmentPatient(models.TransientModel):

    _name = 'medical.surgical.appointment.patient'

    appointment_id = fields.Many2one(
        'medical.surgical.appointment',
        required=True,
    )
    # search fields
    patient_ids = fields.Many2many(
        'medical.patient',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        appointment = self.env.context.get('medical_appointment', False)
        if not appointment:
            return res
        appointment = self.env['medical.surgical.appointment'].browse(
            appointment
        )
        res['appointment_id'] = appointment.id
        patients = self.env['medical.patient'].search(
            [
                ('name', '=ilike', appointment.patient_name),
            ]
        )
        res['patient_ids'] = [(6, 0, patients.ids)]
        return res

    def generate_encounter_new_patient(self):
        self.ensure_one()
        self.appointment_id.patient_id = False
        self.appointment_id.with_context(
            generate_from_wizard=True
        ).generate_encounter()
