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
            'surgical_appointment_time': 1.5,
            'patient_interned': True,
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

    def test_surgical_appointment_workflow(self):
        msa = self.env['medical.surgical.appointment'].create({
            'location_id': self.location.id,
            'surgeon_id': self.practitioner1.id,
            'start_date': fields.Datetime.now(),
            'duration': 1.5,
        })
        self.assertEqual(msa.state, 'draft')
        msa.waiting2confirm_reservation()
        self.assertEqual(msa.state, 'confirmed_reservation')
        with self.assertRaises(ValidationError):
            msa.confirm_reservation2confirm_patient()
        assign_patient = self.env[
            'medical.surgical.appointment.patient'
        ].with_context(active_id=msa.id).create({
            'patient_ids': [(6, 0, [self.patient.id])]
        })
        assign_patient.patient_ids[0].assign_surgical_appointment(
            context={'active_id': msa.id}
        )
        self.assertEqual(msa.patient_id.id, self.patient.id)
        with self.assertRaises(ValidationError):
            msa.confirm_reservation2confirm_patient()
        msa.write({
            'service_id': self.service.id,
            'payor_id': self.payor1.id,
            'coverage_template_id': self.template1.id,
            'subscriber_id': 123421,
            'authorization_number': 123445,
        })
        msa._onchange_service()
        msa._onchange_payor()
        self.assertTrue(msa.patient_interned)
        msa.confirm_reservation2confirm_patient()
        self.assertEqual(msa.state, 'confirmed_patient')

    def test_generate_encounter(self):
        w_type = self.env['workflow.type'].create({
            'name': 'TEST',
            'model_id': self.browse_ref(
                'medical_administration.model_medical_patient').id,
            'model_ids': [(4, self.browse_ref(
                'medical_administration.model_medical_patient').id)],
        })
        plan_definition = self.env['workflow.plan.definition'].create({
            'name': 'Plan definition',
            'type_id': w_type.id,
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
            'patient_id': self.patient.id,
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
        msa.generate_encounter()
        self.assertTrue(msa.encounter_id)
        self.assertEqual(msa.state, 'arrived')
        msa.cancel_appointment()
        self.assertEqual(msa.state, 'cancelled')
        msa.back_to_draft()
        self.assertEqual(msa.state, 'draft')
        self.assertFalse(msa.selected_patient, 'draft')

    def test_location_surgeon_constrains(self):
        self.env['medical.surgical.appointment'].create({
            'location_id': self.location.id,
            'surgeon_id': self.practitioner1.id,
            'start_date': '2019-12-20 08:00:00',
            'duration': 1.5,
        })
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'location_id': self.location.id,
                'surgeon_id': self.practitioner2.id,
                'start_date': '2019-12-20 09:00:00',
                'duration': 1.5,
            })
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'location_id': self.location2.id,
                'surgeon_id': self.practitioner1.id,
                'start_date': '2019-12-20 09:00:00',
                'duration': 1.5,
            })

        # Duration cant be 0 minutes
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'location_id': self.location2.id,
                'surgeon_id': self.practitioner1.id,
                'start_date': '2019-12-20 12:00:00',
                'duration': 0.0,
            })

    def test_appointment_rules(self):
        self.env['medical.surgical.appointment.rule'].create({
            'name': 'No Sundays from 10h to 14h',
            'location_id': self.location.id,
            'rule_type': 'day',
            'is_blocking': True,
            'week_day': '6',
            'hour_from': 10,
            'hour_to': 14,
        })
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'location_id': self.location.id,
                'surgeon_id': self.practitioner1.id,
                'start_date': '2019-10-06 13:00:00',
                'duration': 1.5,
            })

        msar = self.env['medical.surgical.appointment.rule'].create({
            'name': 'Mondays to Practitioner 1',
            'location_id': self.location.id,
            'rule_type': 'surgeon',
            'surgeon_ids': [(6, 0, [self.practitioner1.id])],
            'week_day': '0',
            'all_day': True,
            'validity_stop': '2019-10-10',
        })
        msar._onchange_rule_type()
        self.assertFalse(msar.is_blocking)
        # No warning (correct surgeon)
        msa1 = self.env['medical.surgical.appointment'].create({
            'location_id': self.location.id,
            'surgeon_id': self.practitioner1.id,
            'start_date': '2019-10-07 10:00:00',
            'duration': 1.5,
        })
        # Warning: Reserved to Practitioner 1
        msa2 = self.env['medical.surgical.appointment'].create({
            'location_id': self.location.id,
            'surgeon_id': self.practitioner2.id,
            'start_date': '2019-10-07 15:00:00',
            'duration': 1.5,
        })
        # No warning, rule already expired
        msa3 = self.env['medical.surgical.appointment'].create({
            'location_id': self.location.id,
            'surgeon_id': self.practitioner2.id,
            'start_date': '2019-10-14 15:00:00',
            'duration': 1.5,
        })
        self.assertFalse(msa1.warning)
        self.assertFalse(msa3.warning)
        self.assertEqual(
            msa2.warning,
            'Warning: You are ignoring the'
            ' following rules:\n- Mondays to Practitioner 1'
        )

        calendar_data = msar.get_rules_date_location(
            msa2.start_date,
            msa2.end_date,
            msa2.location_id.id,
        )
        self.assertEqual(calendar_data[0]['name'], msar.name)

        msar = self.env['medical.surgical.appointment.rule'].create({
            'name': 'Close on 9th October 2019 from 10 to 14',
            'location_id': self.location.id,
            'rule_type': 'specific',
            'specific_from': '2019-10-09 10:00:00',
            'specific_to': '2019-10-09 14:00:00',
            'is_blocking': True,
        })
        msar._onchange_rule_type()
        with self.assertRaises(ValidationError):
            self.env['medical.surgical.appointment'].create({
                'location_id': self.location.id,
                'surgeon_id': self.practitioner1.id,
                'start_date': '2019-10-09 13:00:00',
                'duration': 1.5,
            })
