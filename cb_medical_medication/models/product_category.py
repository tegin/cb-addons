# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    medication = fields.Many2one(
        'product.product',
        domain=[('type', '=', 'service')]
    )
