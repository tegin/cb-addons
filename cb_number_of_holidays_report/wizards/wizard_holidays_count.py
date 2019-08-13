# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class WizardHolidaysCount(models.TransientModel):

    _name = 'wizard.holidays.count'

    name = fields.Char()

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    employee_ids = fields.Many2many('hr.employee')

    department_id = fields.Many2one(
        'hr.department', string='Department'
    )
    category_ids = fields.Many2many(
        'hr.employee.category', string='Tag'
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.employee_ids:
            res[
                'department_id'
            ] = self.env.user.employee_ids[0].department_id.id
        return res

    def _prepare_employee_domain(self):
        res = []
        if self.category_ids:
            res.append(('category_ids', 'in', self.category_ids.ids))
        if self.department_id:
            res.append(('department_id', 'child_of', self.department_id.id))
        return res

    @api.multi
    def populate(self):
        domain = self._prepare_employee_domain()
        self.employee_ids = self.env['hr.employee'].search(domain)
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        if not data.get('employee_ids'):
            raise UserError(_(
                'You have to select at least one Employee. And try again.'))
        datas = {
            'ids': self.ids,
            'model': self._name,
            'form': data
        }
        return self.env.ref(
            'cb_number_of_holidays_report.action_report_holidays_count'
        ).report_action(self, data=datas)

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        for record in self:
            if (record.date_from and record.date_to and
                    record.date_from > record.date_to):
                raise ValidationError(
                    _('The start date must be anterior to the end date.'))
