# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.partner_id.employee_ids:
            res.partner_id.employee_ids._compute_user()
        return res
