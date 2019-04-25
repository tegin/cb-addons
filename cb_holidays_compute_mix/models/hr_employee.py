# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    @api.multi
    def action_view_leaves_left(self):
        action = self.env.ref(
            'cb_holidays_compute_mix.action_view_leaves_left')
        result = action.read()[0]
        return result
