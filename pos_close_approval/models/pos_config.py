# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    requires_approval = fields.Boolean(default=False)

    def closed_states(self):
        res = super(PosConfig, self).closed_states()
        res.append('pending_approval')
        return res
