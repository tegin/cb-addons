# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLaboralCategory(models.Model):

    _name = 'hr.laboral.category'
    _description = 'Hr Laboral Category'

    name = fields.Char()
