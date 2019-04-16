# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrHolidays(models.Model):

    _inherit = 'hr.holidays'

    warning = fields.Char(compute='_compute_warning_range')

    @api.depends('holiday_status_id', 'date_from', 'date_to')
    def _compute_warning_range(self):
        if self.type == 'remove' and self.holiday_status_id and\
                self.holiday_status_id.cb_personal_day:
            if self.date_from and self.date_to:
                year = int(fields.Datetime.from_string(self.date_from).year)
                interval = self.env['hr.holidays.status.ranges'].search([
                    ('status_id', '=', self.holiday_status_id.id),
                    ('year', '=', year),
                ], limit=1)
                if interval:
                    interval_from = fields.Datetime.to_string(
                        fields.Date.from_string(interval.date_from)
                    )
                    interval_to = fields.Datetime.to_string(
                        fields.Date.from_string(interval.date_to)
                    )
                    if self.date_from < interval_from or \
                            self.date_to > interval_to:
                        self.warning = _(
                            'The selected dates '
                            'are out of this holiday type\'s '
                            'range. (%s - %s)')\
                                       % (interval.date_from, interval.date_to)
                        return
        self.warning = False
