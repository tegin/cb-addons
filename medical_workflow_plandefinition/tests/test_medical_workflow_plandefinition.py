# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalWorkflowPlandefinition(TransactionCase):

    def setUp(self):
        super(TestMedicalWorkflowPlandefinition, self).setUp()
        self.type_model = self.env['workflow.type']
        self.act_def_model = self.env['workflow.activity.definition']
        self.action_model = self.env['workflow.plan.definition.action']
        self.plan_model = self.env['workflow.plan.definition']
        self.type_1 = self._create_type()
        self.act_def_1 = self._create_act_def()
        self.action_1 = self._create_action()
        self.plan_1 = self._create_plan()

    def _create_type(self):
        return self.type_model.create({
            'name': 'Test type',
            'model_id': self.browse_ref(
                'medical_administration.model_medical_patient').id,
            'model_ids': [(4, self.browse_ref(
                'medical_administration.model_medical_patient').id)],
        })

    def _create_act_def(self):
        return self.act_def_model.create({
            'name': 'Test activity',
            'model_id': self.type_1.model_id.id,
        })

    def _create_action(self):
        return self.action_model.create({
            'name': 'Test action',
            'activity_definition_id': self.act_def_1.id,
            'type_id': self.type_1.id,
        })

    def _create_plan(self):
        return self.plan_model.create({
            'name': 'Test plan',
            'direct_action_ids': self.action_1,
            'type_id': self.type_1.id,
        })

    def test_medical_plan_definition(self):
        self.assertTrue(self.plan_1.is_billable)
        self.assertTrue(self.plan_1.is_breakdown)
        self.assertTrue(self.action_1.is_billable)
