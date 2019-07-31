# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HrHolidays(models.Model):

    _name = 'hr.holidays'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'hr.holidays']
