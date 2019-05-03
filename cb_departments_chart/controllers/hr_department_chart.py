# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class HrOrgChartController(http.Controller):
    _departments_level = 2  # FP request

    def _prepare_department_data(self, department):
        return dict(
            id=department.id,
            name=department.name,
            link='/mail/view?model=hr.department&res_id=%s' % department.id,
            manager_id=department.manager_id.id,
            manager_name=department.manager_id.name or '',
            direct_sub_count=len(department.child_ids),
            indirect_sub_count=department.child_all_count,
        )

    @http.route('/cb_departments_chart/get_org_chart',
                type='json',
                auth='user')
    def get_org_chart(self, department_id):
        if not department_id:
            return{}
        department_id = int(department_id)
        Department = request.env['hr.department']
        # check and raise
        if not Department.check_access_rights('read', raise_exception=False):
            return {}
        try:
            Department.browse(department_id).check_access_rule('read')
        except AccessError:
            return {}
        else:
            department = Department.browse(department_id)

        # compute employee data for org chart
        ancestors, current = request.env['hr.department'], department
        while current.parent_id:
            ancestors += current.parent_id
            current = current.parent_id

        values = dict(
            self=self._prepare_department_data(department),
            departments=[self._prepare_department_data(ancestor)
                         for idx, ancestor
                         in enumerate(ancestors)
                         if idx < self._departments_level],
            departments_more=len(ancestors) > self._departments_level,
            children=[self._prepare_department_data(child)
                      for child in department.child_ids],
        )
        values['departments'].reverse()
        return values
