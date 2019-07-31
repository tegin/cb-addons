# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrHolidays(models.Model):

    _name = 'hr.holidays'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'hr.holidays']

    @api.multi
    def _prepare_holidays_meeting_values(self):
        result = super()._prepare_holidays_meeting_values()
        if not result.get('partner_ids', False):
            result['partner_ids'] = [(4, self.employee_id.partner_id.id)]
        return result
