from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    third_party_order = fields.Boolean(
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]}, )
    third_party_partner_id = fields.Many2one(
        comodel_name='res.partner',
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain=[
            ('supplier', '=', True),
            ('third_party_sequence_id', '!=', False)],
    )
    third_party_number = fields.Char(copy=False, readonly=True)
    third_party_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Third party move',
        readonly=True,
    )
    source_third_party_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Third party order',
        readonly=True)
    third_party_order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='source_third_party_order_id',
        string='Third party orders',
        readonly=True)
    third_party_order_count = fields.Integer(
        string='Third party order #',
        compute='_compute_third_party_order_count',
        readonly=True)

    @api.multi
    def _compute_third_party_order_count(self):
        for order in self:
            order.third_party_order_count = len(order.third_party_order_ids)

    def create_third_party_move(self):
        self.third_party_move_id = self.env['account.move'].create(
            self._third_party_move_vals())

    def _third_party_move_vals(self):
        journal = self.company_id.third_party_journal_id
        if not journal:
            journal = self.env['account.journal'].search([
                ('company_id', '=', self.company_id.id),
                ('type', '=', 'general')
            ], limit=1)
        return {
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': self.partner_id.name,
                    'partner_id': self.partner_id.id,
                    'account_id': self.partner_id.with_context(
                        force_company=self.company_id.id
                    ).property_third_party_customer_account_id.id,
                    'debit': self.amount_total,
                    'credit': 0,
                }),
                (0, 0, {
                    'name': self.third_party_partner_id.name,
                    'partner_id': self.third_party_partner_id.id,
                    'account_id': self.third_party_partner_id.with_context(
                        force_company=self.company_id.id
                    ).property_third_party_supplier_account_id.id,
                    'debit': 0,
                    'credit': self.amount_total,
                }),
            ]
        }

    @api.model
    def _prepare_third_party_order(self):
        lines = self.order_line.filtered(lambda l: l.third_party_product_id)
        so_lines = [(0, 0, {
            'name': l.product_id.name,
            'product_id': l.third_party_product_id.id,
            'product_uom_qty': l.product_uom_qty,
            'product_uom': l.product_uom.id,
            'price_unit': l.third_party_price,
        }) for l in lines]

        return {
            'partner_id': self.third_party_partner_id.id,
            'order_line': so_lines,
            'source_third_party_order_id': self.id,
        }

    @api.model
    def _create_third_party_order(self):
        vals = self._prepare_third_party_order()
        return self.env['sale.order'].create(vals)

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self.filtered(lambda o: o.third_party_order):
            order.create_third_party_move()
            order._create_third_party_order()
        return res

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if self.filtered(lambda o: o.third_party_order):
                order.action_done()
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self.filtered(lambda o: o.third_party_move_id):
            order.third_party_order_id.action_cancel()
            order.third_party_move_id.button_cancel()
            order.third_party_move_id.unlink()
        return res

    def action_view_third_party_order(self):
        action = self.env.ref('sale.action_orders')
        result = action.read()[0]
        order_ids = self.third_party_order_ids.ids
        if len(order_ids) != 1:
            result['domain'] = [('id', 'in', order_ids)]
        elif len(order_ids) == 1:
            res = self.env.ref('sale.view_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = order_ids[0]
        return result


class SalerOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.third_party_order')
    def _compute_invoice_status(self):
        for line in self:
            line.invoice_status = 'no'

    third_party_order = fields.Boolean(
        related='order_id.third_party_order'
    )
    third_party_price = fields.Monetary(
        currency_field='currency_id'
    )
    third_party_product_id = fields.Many2one(
        'product.product',
    )
