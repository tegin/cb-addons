# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAttendanceTheoreticalTimeReport(models.Model):
    _inherit = "hr.attendance.theoretical.time.report"

    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id',
    )
    week_day = fields.Selection([
        (0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
        (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'),
    ])
    is_public_holiday = fields.Boolean()

    def _select(self):
        result = super()._select()
        result += ", extract(dow from date) as week_day, is_public_holiday "
        return result

    def _select_sub1(self):
        result = super()._select_sub1()
        result += ', line is not null as is_public_holiday'
        return result

    def _select_sub2(self):
        result = super()._select_sub2()
        result += ', line is not null as is_public_holiday'
        return result

    def _from_sub1(self):
        result = super()._from_sub1()
        result += """
            INNER JOIN hr_employee as he ON he.id = ha.employee_id
            LEFT JOIN res_partner as p on p.id = he.address_id
            LEFT JOIN (
                hr_holidays_public as public
                INNER JOIN hr_holidays_public_line as line ON
                    line.year_id = public.id
                LEFT JOIN hr_holiday_public_state_rel as st ON
                    line.id = st.line_id
            ) ON
                (public.country_id is NULL OR public.country_id = p.country_id)
                AND line.date = ha.check_in::date
                AND (st is NULL OR st.state_id = p.state_id)
            """
        return result

    def _from_sub2(self):
        result = super()._from_sub2()

        result += """
            LEFT JOIN res_partner as p on p.id = he.address_id
            LEFT JOIN (
                hr_holidays_public as public
                INNER JOIN hr_holidays_public_line as line ON
                    line.year_id = public.id
                LEFT JOIN hr_holiday_public_state_rel as st ON
                    line.id = st.line_id
            ) ON
                (public.country_id is NULL OR public.country_id = p.country_id)
                AND line.date = gs::date
                AND (st is NULL OR st.state_id = p.state_id)
            """
        return result

    def _group_by(self):
        result = super()._group_by()
        result += ', is_public_holiday '
        return result
