from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    third_party_order = fields.Boolean(
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]}, )
    third_party_partner_id = fields.Many2one(
        'res.partner',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[
            ('supplier', '=', True),
            ('third_party_sequence_id', '!=', False)],
    )
    third_party_number = fields.Char(copy=False, readonly=True)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        for so in self.filtered(
                lambda r: r.third_party_order and not r.third_party_number
        ):
            so.third_party_number = \
                so.third_party_partner_id.third_party_sequence_id.next_by_id()
            so.action_done()
        return super().action_invoice_create(grouped, final)

    @api.multi
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.third_party_order:
            partner = self.third_party_partner_id
            res.update({
                'account_id': partner.property_account_receivable_id.id,
                'partner_id': partner.id,
                'fiscal_position_id': partner.property_account_position_id.id,
            })
        return res


class SalerOrderLine(models.Model):
    _inherit = 'sale.order.line'

    third_party_order = fields.Boolean(
        related='order_id.third_party_order'
    )
    third_party_price = fields.Monetary(
        currency_field='currency_id'
    )
    third_party_product_id = fields.Many2one(
        'product.product',
    )

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super()._prepare_invoice_line(qty=qty)
        if self.order_id.third_party_order:
            product = self.third_party_product_id or self.product_id
            account = (product.property_account_income_id or
                       product.categ_id.property_account_income_categ_id)
            if not account:
                raise UserError(_(
                    'Please define expense account for this product: "%s" '
                    '(id:%d) - or for its category: "%s".'
                ) % (
                    self.product_id.name, self.product_id.id,
                    self.product_id.categ_id.name
                ))

            fpos = self.order_id.third_party_partner_id.\
                property_account_position_id
            if fpos:
                account = fpos.map_account(account)
            taxes = product.taxes_id.filtered(
                lambda r: r.company_id == self.company_id
            )
            res.update({
                'product_id': product.id,
                'uom_id': product.uom_id.id,
                'account_id': account.id,
                'price_unit': self.third_party_price or 0.,
                'invoice_line_tax_ids': [(6, 0, taxes.ids)],
            })
        return res
