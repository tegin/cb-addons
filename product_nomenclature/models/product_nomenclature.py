from odoo import api, fields, models, _


class ProductNomenclature(models.Model):
    _name = 'product.nomenclature'

    code = fields.Char(required=True)
    name = fields.Text(required=True)
    item_ids = fields.One2many(
        'product.nomenclature.product',
        inverse_name='nomenclature_id'
    )
    active = fields.Boolean(default=True)

    @api.multi
    def action_view_items(self):
        action = self.env.ref('product_nomenclature.'
                              'product_nomenclature_product_action')
        result = action.read()[0]
        result['context'] = {'default_nomenclature_id': self.id}
        result['domain'] = [('nomenclature_id', '=', self.id)]
        return result


class ProductNomenclatureProduct(models.Model):
    _name = 'product.nomenclature.product'

    nomenclature_id = fields.Many2one(
        'product.nomenclature',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        required=True
    )
    code = fields.Char(required=True)
    name = fields.Char(required=True)

    _sql_constraints = [(
        'product_nomenclature_unique',
        'unique(product_id, nomenclature_id)',
        _('Product must be unique in a nomenclature'))
    ]

    @api.onchange('product_id')
    def _onchange_product_template(self):
        if not self.name:
            self.name = self.product_id.name
        if not self.code:
            self.code = self.product_id.default_code
