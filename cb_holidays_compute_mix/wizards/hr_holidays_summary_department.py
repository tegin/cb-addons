# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HolidaysSummaryDept(models.TransientModel):

    _inherit = 'hr.holidays.summary.dept'

    is_officer = fields.Boolean(readonly=True)

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        is_officer = self.env['res.users'].has_group(
            'hr.group_hr_user'
        ) and not self.env['res.users'].has_group('hr.group_hr_manager')
        if is_officer:
            vals_list = self.env['hr.department'].search([
                ('manager_id', '!=', False),
                ('manager_id.user_id', '=', self.env.user.id),
            ]).ids
            if len(vals_list) == 0:
                raise UserError(_(
                    'In order to create department reports you must be '
                    'manager of at least one department'))
            rec.update({
                'depts': [(6, 0, vals_list)],
                'is_officer': True,
            })
        return rec
