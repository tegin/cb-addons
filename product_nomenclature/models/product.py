from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    nomenclature_ids = fields.One2many(
        'product.nomenclature.product',
        inverse_name='product_id'
    )
