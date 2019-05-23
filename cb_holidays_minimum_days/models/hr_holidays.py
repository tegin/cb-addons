# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    warning_minimum = fields.Char(compute='_compute_warning_minimum')

    @api.depends('holiday_status_id', 'number_of_days_temp', 'employee_id')
    def _compute_warning_minimum(self):
        for rec in self:
            rec.warning = False
            min_days = rec.holiday_status_id.minimum_days
            days_asking = rec.number_of_days_temp
            if (rec.type == 'remove' and
                    rec.holiday_status_id.minimum_days and days_asking):
                if days_asking < min_days:
                    rec.warning_minimum = _(
                        'Warning: The number of days is less than the minimum'
                        ' for that holiday type (%s)') % min_days
                    continue
                if rec.employee_id:
                    leave_days = rec.holiday_status_id.get_days(
                        rec.employee_id.id)[rec.holiday_status_id.id]
                    days_left = min(
                        leave_days['remaining_leaves'],
                        leave_days['virtual_remaining_leaves']
                    ) - days_asking
                    if 0 < days_left < min_days:
                        rec.warning_minimum = _(
                            'Warning: The number of days remaining (%s)'
                            ' will be less than the minimum for that'
                            ' holiday type (%s)' % (int(days_left), min_days)
                        )
