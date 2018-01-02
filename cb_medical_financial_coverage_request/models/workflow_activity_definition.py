# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ActivityDefinition(models.Model):
    # FHIR entity: Activity Definition
    # (https://www.hl7.org/fhir/activitydefinition.html)
    _inherit = 'workflow.activity.definition'

    def _get_activity_values(self, vals, parent=False, plan=False, action=False
                             ):
        coverage_id = vals['coverage_id']
        coverage = self.env['medical.coverage'].browse([coverage_id])
        template_id = coverage.coverage_template_id
        agreements = self.env['medical.coverage.agreement'].search(
            [('coverage_template_ids', 'in', [template_id.id])])
        agreement_item_id = self.env['medical.coverage.agreement.item'].\
            search([
                ('coverage_agreement_id', 'in', agreements.ids),
                ('product_id', '=', self.service_id.id),
            ])
        vals['coverage_agreement_id'] = \
            agreement_item_id.coverage_agreement_id.id or False
        vals['coverage_agreement_item_id'] = agreement_item_id.id or False
        return super(ActivityDefinition, self)._get_activity_values(
            vals, parent=False, plan=False, action=False)
