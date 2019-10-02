# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceCalendar(models.Model):

    _inherit = "resource.calendar"

    company_id = fields.Many2one(default=False)
