from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nomenclature_ids = fields.One2many(
        'product.nomenclature.product',
        inverse_name='product_template_id'
    )
