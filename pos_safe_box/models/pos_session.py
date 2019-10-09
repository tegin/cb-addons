# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    pos_session_validation_id = fields.Many2one(
        "pos.session.validation", readonly=True
    )

    @api.multi
    def action_pos_session_close(self):
        res = super(PosSession, self).action_pos_session_close()
        for session in self:
            sbg = session.config_id.safe_box_group_id
            if sbg:
                self.pos_session_validation_id = (
                    sbg.get_current_session_validation()
                )
        return res
