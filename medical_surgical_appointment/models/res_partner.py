# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    allow_surgical_appointment = fields.Boolean(
        string='Allow Surgical Appointment',
    )
