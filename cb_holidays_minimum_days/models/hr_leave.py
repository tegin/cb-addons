# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrHolidays(models.Model):
    _inherit = "hr.leave"

    warning_minimum = fields.Char(compute='_compute_warning_minimum')

    @api.depends('holiday_status_id', 'employee_id',
                 'number_of_days_display', 'number_of_hours_display')
    def _compute_warning_minimum(self):
        for rec in self:
            rec.warning = False
            min_time = rec.holiday_status_id.minimum_time
            time_asking = rec.number_of_days_display if (
                rec.leave_type_request_unit == 'day'
            ) else rec.number_of_hours_display
            if rec.holiday_status_id.minimum_time:
                if time_asking < min_time:
                    rec.warning_minimum = _(
                        'Warning: The number of %ss requested is less '
                        'than the minimum for that holiday type (%s)') % (
                        rec.leave_type_request_unit, min_time
                    )
                    continue
                if rec.employee_id:
                    leave_days = rec.holiday_status_id.get_days(
                        rec.employee_id.id)[rec.holiday_status_id.id]
                    time_left = min(
                        leave_days['remaining_leaves'],
                        leave_days['virtual_remaining_leaves']
                    ) - time_asking
                    if 0 < time_left < min_time:
                        rec.warning_minimum = _(
                            'Warning: The number of %ss remaining (%s)'
                            ' will be less than the minimum for that'
                            ' holiday type (%s)' % (
                                rec.leave_type_request_unit,
                                int(time_left),
                                min_time
                            )
                        )
