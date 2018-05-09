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
        self.ensure_one()
        if self.third_party_order:
            journal_id = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ]).id
            return {
                'name': self.client_order_ref or '',
                'origin': self.name,
                'type': 'in_invoice',
                'account_id':
                    self.partner_invoice_id.property_account_payable_id.id,
                'partner_id': self.third_party_partner_id.id,
                'journal_id': journal_id,
                'currency_id': self.pricelist_id.currency_id.id,
                'comment': self.note,
                'payment_term_id': self.payment_term_id.id,
                'fiscal_position_id':
                    self.fiscal_position_id.id or
                    self.partner_invoice_id.property_account_position_id.id,
                'company_id': self.company_id.id,
                'user_id': self.user_id and self.user_id.id,
                'team_id': self.team_id.id
            }
        return super()._prepare_invoice()

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoiced(self):
        res = super()._get_invoiced()
        for order in self.filtered(lambda r: r.third_party_order):
            invoice_ids = order.order_line.mapped('invoice_lines').mapped(
                'invoice_id').filtered(
                lambda r: r.type in ['in_invoice', 'in_refund'])
            refunds = invoice_ids.search([('origin', 'like', order.name), (
                'company_id', '=', order.company_id.id)]).filtered(
                lambda r: r.type in ['in_invoice', 'in_refund'])
            invoice_ids |= refunds.filtered(
                lambda r: order.name in [origin.strip() for origin in
                                         r.origin.split(',')])
            # Search for refunds as well
            refund_ids = self.env['account.invoice'].browse()
            if invoice_ids:
                for inv in invoice_ids:
                    refund_ids += refund_ids.search(
                        [('type', '=', 'in_refund'),
                         ('origin', '=', inv.number),
                         ('origin', '!=', False),
                         ('journal_id', '=', inv.journal_id.id)])
            order.update({
                'invoice_count': len(set(invoice_ids.ids + refund_ids.ids)),
                'invoice_ids': invoice_ids.ids + refund_ids.ids,
            })
            return
        return res

    @api.multi
    def action_view_invoice(self):
        if self == self.filtered(lambda r: r.third_party_order):
            invoices = self.mapped('invoice_ids')
            action = self.env.ref('account.action_invoice_tree2').read()[0]
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                action['views'] = [
                    (self.env.ref('account.invoice_supplier_form').id, 'form')]
                action['res_id'] = invoices.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action
        return super().action_view_invoice()


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

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity')
    def _get_invoice_qty(self):
        for line in self.filtered(lambda r: r.order_id.third_party_order):
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines:
                if invoice_line.invoice_id.state != 'cancel':
                    if invoice_line.invoice_id.type == 'in_invoice':
                        qty_invoiced += invoice_line.uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom)
                    elif invoice_line.invoice_id.type == 'in_refund':
                        qty_invoiced -= invoice_line.uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom)
            line.qty_invoiced = qty_invoiced
        return super(SalerOrderLine, self.filtered(
            lambda r: not r.order_id.third_party_order
        ))._get_invoice_qty()

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super()._prepare_invoice_line(qty=qty)
        if self.order_id.third_party_order:
            product = self.third_party_product_id or self.product_id
            account = (product.property_account_expense_id or
                       product.categ_id.property_account_expense_categ_id)
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
            taxes = product.supplier_taxes_id.filtered(
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
