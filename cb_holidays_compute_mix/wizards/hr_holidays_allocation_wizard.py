# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _


class AccountInvoiceRefund(models.TransientModel):

    _name = "hr.holidays.allocation.wizard"

    name = fields.Char(string='Description')
    holiday_status_id = fields.Many2one(
        'hr.holidays.status', string='Leave Type', required=True)
    duration = fields.Float(string='Duration', required=True)
    employee_ids = fields.Many2many(
        'hr.employee', string='Employees', required=True
    )
    count_in_hours = fields.Boolean(
        related='holiday_status_id.count_in_hours',
        readonly=True)
    second_validation = fields.Boolean(
        related='holiday_status_id.double_validation',
        readonly=True)
    approve = fields.Boolean(string='Automatically Approve', default=True)
    department_id = fields.Many2one(
        'hr.department', string='Department'
    )
    category_id = fields.Many2one(
        'hr.employee.category', string='Tag'
    )

    def _prepare_employee_domain(self):
        res = []
        if self.category_id:
            res.append(('category_ids', '=', self.category_id.id))
        if self.department_id:
            res.append(('department_id', '=', self.department_id.id))
        return res

    @api.multi
    def populate(self):
        domain = self._prepare_employee_domain()
        employees = self.env['hr.employee'].search(domain)
        self.employee_ids = employees
        action = {
            'name': _('Create Allocations'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.holidays.allocation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context,
        }
        return action

    @api.multi
    def create_allocations(self):
        for form in self:
            for employee in form.employee_ids:
                allocation = self.env['hr.holidays'].create(
                    {
                        'name': form.name,
                        'holiday_status_id': form.holiday_status_id.id,
                        'holiday_type': 'employee',
                        'employee_id': employee.id,
                        'department_id': employee.department_id.id,
                        'type': 'add'
                    }
                )
                if form.count_in_hours:
                    allocation.write({'number_of_hours_temp': form.duration})
                else:
                    allocation.write({'number_of_days_temp': form.duration})

                if form.approve:
                    allocation.action_approve()
                    if form.second_validation:
                        allocation.action_validate()
                import logging
                logging.info('creadaa')
