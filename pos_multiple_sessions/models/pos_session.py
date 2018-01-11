# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.constrains('user_id', 'state')
    def _check_unicity(self):
        return
