# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardNewMedicalAppointment(models.TransientModel):

    _name = 'wizard.new.medical.appointment'

    name = fields.Char()

    patient_id = fields.Many2one(
        string='Patient',
        comodel_name='medical.patient',
    )

    service_id = fields.Many2one(
        string='Service',
        comodel_name='product.product',
        required=True,
        domain=[('type', '=', 'service'),
                ('allow_surgical_appointment', '=', True)],
    )

    location_id = fields.Many2one(
        string="Location",
        comodel_name='res.partner',
        required=True,
        domain=[
            ('is_location', '=', True),
            ('allow_surgical_appointment', '=', True)
        ],
    )

    start_date = fields.Datetime(
        string='Start Date',
    )

    # Practitioners

    surgeon_id = fields.Many2one(
        'res.partner',
        domain=[('allow_surgical_appointment', '=', True),
                ('is_practitioner', '=', True)],
        string='Surgeon',
        required=True,
    )
    aux_surgeon_id = fields.Many2one(
        'res.partner',
        domain=[('allow_surgical_appointment', '=', True),
                ('is_practitioner', '=', True)],
        string='Auxiliary Surgeon',
    )

    @api.multi
    def doit(self):
        if not self.surgeon_id:
            raise ValidationError(_('You Must Select a Surgeon'))
        patient_id = self.patient_id.id if self.patient_id else False
        aux_surgeon_id = self.aux_surgeon_id.id if (
            self.aux_surgeon_id
        ) else False
        context = {
            'patient_id': patient_id,
            'location_id': self.location_id.id,
            'service_id': self.service_id.id,
            'surgeon_id': self.surgeon_id.id,
            'aux_surgeon_id': aux_surgeon_id,
        }
        env_context = self.env.context.copy()
        env_context.update(context)
        self.env.context = context
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Select Dates',
            'res_model': 'medical.surgical.appointment',
            'view_mode': 'calendar',
            'context': self.env.context,
            'target': 'new',
            'domain': "[('state', 'not in', ['draft', 'cancelled'])]"
        }
        return action
