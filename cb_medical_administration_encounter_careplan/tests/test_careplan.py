# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestEncounter(TransactionCase):
    def setUp(self):
        super(TestEncounter, self).setUp()
        self.patient = self.env['medical.patient'].create({
            'name': 'Patient'
        })

    def test_create_careplan(self):
        encounter = self.env['medical.encounter'].create({
            'patient_id': self.patient.id
        })
        res = encounter.create_careplan()
        careplan = self.env['medical.careplan'].browse([res.get('res_id')])
        self.assertNotEqual(careplan, False)
        self.assertEqual(careplan.encounter_id, encounter)
        self.assertEqual(careplan.patient_id, encounter.patient_id)
