# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CustomInfoProperty(models.Model):
    _inherit = "custom.info.property"

    compute_form_value = fields.Char()
