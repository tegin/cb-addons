# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAttendanceTheoreticalTimeReport(models.Model):
    _inherit = "hr.attendance.theoretical.time.report"

    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id',
    )
