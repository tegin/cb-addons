# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCareplanAddPlanDefinition(models.TransientModel):
    _inherit = 'medical.careplan.add.plan.definition'

    coverage_id = fields.Many2one(
        'medical.coverage',
        related='careplan_id.coverage_id'
    )

    service_id = fields.Many2one(
        'product.product'
    )

    plan_definition_id = fields.Many2one(
        comodel_name='workflow.plan.definition',
        compute='_compute_plan_definition_id',
        required=True
    )

    def _compute_plan_definition_id(self):
        agreement = self.env['medical.coverage.agreement.item'].search([
            ('coverage_agreement_id', 'in', self.coverage_id.coverage_template_id.agreement_ids.ids),
            ('product_id', '=', self.service_id.id)
        ])
        agreement.ensure_one()
        self.plan_definition_id = agreement.plan_definition_id

    def _get_values(self):
        values = super(MedicalCareplanAddPlanDefinition, self)._get_values()
        values['coverage_id'] = self.careplan_id.coverage_id.id
        return values
