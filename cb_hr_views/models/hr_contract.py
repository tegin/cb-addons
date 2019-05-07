# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrContract(models.Model):

    _inherit = 'hr.contract'

    working_hours_type = fields.Selection(
        selection=[('full', 'Full Time'),
                   ('part', 'Part time'),
                   ('reduced', 'Reduced')],
        string='Working Hours Type',
        default='full'
    )
    percentage_of_reduction = fields.Integer('Percentage of Reduction')

    substituting_id = fields.Many2one('hr.employee', 'Substituting')
    substitute_contract = fields.Boolean(related='type_id.substitute_contract')

    @api.onchange('type_id')
    def _onchange_type_id(self):
        for record in self:
            if not record.type_id.substitute_contract:
                record.substituting_id = False


class ContractType(models.Model):

    _inherit = 'hr.contract.type'
    substitute_contract = fields.Boolean(
        string='Substitute Contract',
        help='Check if this is a substitution contract'
    )
