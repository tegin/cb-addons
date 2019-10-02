# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields


class TestMedicalSurgicalAppointment(TransactionCase):

    def setUp(self):
        super(TestMedicalSurgicalAppointment, self).setUp()
        self.patient = self.env['medical.patient'].create({
            'firstname': 'Pieter',
            'lastname': 'Parker',
            'lastname2': 'Parker',
            'vat': '1234567889',
            'mobile': '67898765',
        })
        self.service = self.env['product.product'].create({
            'name': 'Service',
            'type': 'service',
            'allow_surgical_appointment': True,
        })

        self.practitioner1 = self.env['res.partner'].create({
            'name': 'Practitioner1',
            'is_medical': True,
            'is_practitioner': True,
            'allow_surgical_appointment': True,
        })
        self.practitioner2 = self.env['res.partner'].create({
            'name': 'Practitioner2',
            'is_medical': True,
            'is_practitioner': True,
            'allow_surgical_appointment': True,
        })
        self.center = self.env['res.partner'].create({
            'name': 'Center',
            'is_medical': True,
            'is_center': True,
            'encounter_sequence_prefix': 'Test Center Prefix'
        })
        self.location = self.env['res.partner'].create({
            'name': 'Location',
            'center_id': self.center.id,
            'is_medical': True,
            'is_location': True,
            'allow_surgical_appointment': True,
        })
        self.location2 = self.env['res.partner'].create({
            'name': 'Location2',
            'center_id': self.center.id,
            'is_medical': True,
            'is_location': True,
            'allow_surgical_appointment': True,
        })
        # Creating 2 payors to test onchange
        self.payor1 = self.env['res.partner'].create({
            'name': 'Payor 1',
            'is_payor': True,
        })
        self.template1 = self.env['medical.coverage.template'].create({
            'payor_id': self.payor1.id,
            'name': 'Coverage 1',
        })
        self.payor2 = self.env['res.partner'].create({
            'name': 'Payor 1',
            'is_payor': True,
        })
        self.template2 = self.env['medical.coverage.template'].create({
            'payor_id': self.payor2.id,
            'name': 'Coverage 2',
        })

    def test_create_surgical_appointment_wo_patient(self):
        msa = self.env['medical.surgical.appointment'].create({
            'firstname': self.patient.firstname,
            'mobile': '67898765',
            'service_id': self.service.id,
            'start_date': fields.Datetime.now(),
            'location_id': self.location.id,
            'payor_id': self.payor1.id,
            'coverage_template_id': self.template1.id,
            'duration': 1.5,
            'surgeon_id': self.practitioner1.id,
        })
        self.assertTrue(msa.end_date)

    def test_create_surgical_appointment(self):
        msa = self.env['medical.surgical.appointment'].create({
            'patient_id': self.patient.id,
            'mobile': '67898765',
            'service_id': self.service.id,
            'start_date': fields.Datetime.now(),
            'location_id': self.location.id,
            'payor_id': self.payor1.id,
            'coverage_template_id': self.template1.id,
            'duration': 1.5,
            'surgeon_id': self.practitioner1.id,
        })

        msa._compute_patient_name()
        self.assertEqual(msa.patient_name, 'Parker Parker Pieter')
        self.assertEqual(msa.vat, '1234567889')

        msa.payor_id = self.payor2.id
        msa._onchange_payor()
        self.assertEqual(msa.coverage_template_id.id, self.template2.id)

        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'patient_id': self.patient.id,
                'mobile': '67898765',
                'service_id': self.service.id,
                'start_date': fields.Datetime.now(),
                'location_id': self.location.id,
                'payor_id': self.payor1.id,
                'coverage_template_id': self.template1.id,
                'duration': 1.5,
                'surgeon_id': self.practitioner2.id,
            })
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'patient_id': self.patient.id,
                'mobile': '67898765',
                'service_id': self.service.id,
                'start_date': fields.Datetime.now(),
                'location_id': self.location2.id,
                'payor_id': self.payor1.id,
                'coverage_template_id': self.template1.id,
                'duration': 1.5,
                'surgeon_id': self.practitioner2.id,
                'aux_surgeon_id': self.practitioner1.id,
            })

    def test_workflow_surgical_appointment(self):
        msa = self.env['medical.surgical.appointment'].create({
            'patient_id': self.patient.id,
            'mobile': '67898765',
            'service_id': self.service.id,
            'start_date': fields.Datetime.now(),
            'location_id': self.location.id,
            'payor_id': self.payor1.id,
            'coverage_template_id': self.template1.id,
            'duration': 1.5,
            'surgeon_id': self.practitioner1.id,
        })
        # Workflow
        self.assertEqual(msa.state, 'draft')
        msa.waiting2confirm()
        self.assertEqual(msa.state, 'confirmed')
        msa.cancel_appointment()
        self.assertEqual(msa.state, 'cancelled')
        msa.back_to_draft()
        self.assertEqual(msa.state, 'draft')

    def test_generate_encounter(self):
        type = self.env['workflow.type'].create({
            'name': 'TEST',
            'model_id': self.browse_ref(
                'medical_administration.model_medical_patient').id,
            'model_ids': [(4, self.browse_ref(
                'medical_administration.model_medical_patient').id)],
        })
        plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan definition',
            'type_id': type.id,
        })
        agreement = self.env['medical.coverage.agreement'].create({
            'name': 'Agreement',
            'center_ids': [(4, self.center.id)],
            'coverage_template_ids': [(4, self.template1.id)],
            'company_id': self.env.user.company_id.id,
            'invoice_group_method_id': self.browse_ref(
                'cb_medical_careplan_sale.by_preinvoicing').id,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })
        self.env[
            'medical.coverage.agreement.item'
        ].create({
            'product_id': self.service.id,
            'plan_definition_id': plan_definition.id,
            'coverage_agreement_id': agreement.id,
            'total_price': 5.0,
            'coverage_percentage': 100.0,
            'authorization_method_id': self.browse_ref(
                'cb_medical_financial_coverage_request.without').id,
            'authorization_format_id': self.browse_ref(
                'cb_medical_financial_coverage_request.format_anything').id,
        })

        msa = self.env['medical.surgical.appointment'].create({
            'firstname': 'Generated Patient',
            'mobile': '67898765',
            'service_id': self.service.id,
            'start_date': fields.Datetime.now(),
            'location_id': self.location.id,
            'payor_id': self.payor1.id,
            'coverage_template_id': self.template1.id,
            'duration': 1.5,
            'surgeon_id': self.practitioner1.id,
            'subscriber_id': 123421,
        })
        msa.waiting2confirm()
        msa.with_context(generate_from_wizard=True).generate_encounter()
        self.assertTrue(msa.encounter_id)
        self.assertEqual(msa.state, 'arrived')

        new_patient = self.env['medical.patient'].search([
            ('name', '=', 'Generated Patient')
        ])
        self.assertTrue(new_patient)
