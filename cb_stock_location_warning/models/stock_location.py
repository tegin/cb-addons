# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = 'stock.location'

    warning = fields.Text(string='Warning')
