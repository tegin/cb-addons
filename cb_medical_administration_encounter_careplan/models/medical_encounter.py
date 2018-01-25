# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class MedicalEncounter(models.Model):
    _inherit = 'medical.encounter'

    @api.multi
    def action_view_created_careplan(self, careplan):
        self.ensure_one()
        action = self.env.ref(
            'medical_clinical_careplan.medical_careplan_action')
        result = action.read()[0]
        result['domain'] = "[('careplan_id', '=', " + str(careplan.id) + ")]"
        result['views'] = [(False, 'form')]
        result['res_id'] = careplan.id
        return result

    def get_values(self):
        return {
            'encounter_id': self.id,
            'patient_id': self.patient_id.id,
        }

    def create_careplan(self):
        values = self.get_values()
        careplan = self.env['medical.careplan'].create(values)
        return self.action_view_created_careplan(careplan)
