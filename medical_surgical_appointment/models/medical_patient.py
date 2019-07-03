# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MedicalPatient(models.Model):

    _inherit = 'medical.patient'

    @api.multi
    def assign_surgical_appointment(self, context=False):
        self.ensure_one()
        appointment = context.get(
            'active_id', False
        )
        if isinstance(appointment, int):
            appointment = self.env['medical.surgical.appointment'].browse(
                appointment
            )

        vals = {}
        if self.firstname != appointment.firstname:
            vals.update({'firstname': appointment.firstname})
        if self.lastname != appointment.lastname:
            vals.update({'lastname': appointment.lastname})
        if self.lastname2 != appointment.lastname2:
            vals.update({'lastname2': appointment.lastname2})
        if self.vat != appointment.vat:
            vals.update({'vat': appointment.vat})
        if self.gender != appointment.gender:
            vals.update({'gender': appointment.gender})
        if self.birth_date != appointment.birth_date:
            vals.update({'birth_date': appointment.birth_date})
        if self.phone != appointment.phone:
            vals.update({'phone': appointment.phone})
        if self.mobile != appointment.mobile:
            vals.update({'mobile': appointment.mobile})
        if self.email != appointment.email:
            vals.update({'email': appointment.email})
        self.write(vals)

        appointment.patient_id = self
        appointment.generate_encounter()
