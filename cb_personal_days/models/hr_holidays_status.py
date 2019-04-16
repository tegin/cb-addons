# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrHolidaysStatus(models.Model):

    _inherit = 'hr.holidays.status'

    cb_personal_day = fields.Boolean(string='CB Personal Days')
    ranges = fields.One2many(
        'hr.holidays.status.ranges',
        string='Ranges',
        inverse_name='status_id'
    )
    pending_employees_id = fields.Many2many(
        'hr.employee',
        string='Pending Employees',
        compute='_compute_pending_employees',
        readonly=1,
    )

    @api.depends('ranges')
    def _compute_pending_employees(self):
        vals_list = []
        employees = self.env['hr.employee'].search([])
        for employee in employees:
            data_days = self.get_days(employee.id)
            result = data_days.get(self.id, {})
            remaining_leaves = result.get('remaining_leaves', 0)
            if remaining_leaves > 0:
                vals_list.append(employee.id)
        self.pending_employees_id = [(6, 0, vals_list)]


class HrHolidaysStatusRanges(models.Model):

    _name = 'hr.holidays.status.ranges'
    _order = 'year DESC'

    @api.model
    def _get_default_year(self):
        return int(fields.date.today().year)

    status_id = fields.Many2one('hr.holidays.status')
    year = fields.Integer(string='Year',
                          required=True,
                          default=_get_default_year)

    date_from = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
