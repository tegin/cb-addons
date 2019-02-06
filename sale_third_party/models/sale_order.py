from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


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
    third_party_customer_in_state = fields.Selection([
        ('pending', 'Pending amount'), ('paid', 'Fully paid')
    ], compute='_compute_third_party_residual', store=True, index=True)
    string = 'Incoming payment status',
    third_party_customer_in_residual = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_third_party_residual',
        string='Incoming payment residual amount',
    )
    third_party_customer_in_residual_company = fields.Monetary(
        currency_field='currency_id',
        compute='_compute_third_party_residual',
        string='Incoming payment residual amount in company currency',
    )
    third_party_customer_out_state = fields.Selection([
        ('pending', 'Pending amount'), ('paid', 'Fully paid')
    ], string='Outgoing payment status',
        compute='_compute_third_party_residual', store=True, index=True,)
    third_party_customer_out_residual = fields.Monetary(
        currency_field='currency_id',
        string='Outgoing payment residual amount',
        compute='_compute_third_party_residual',
    )
    third_party_customer_out_residual_company = fields.Monetary(
        currency_field='currency_id',
        string='Outgoing payment residual amount in company currency',
        compute='_compute_third_party_residual',
    )

    @api.multi
    @api.depends("third_party_order", "third_party_move_id",
                 "third_party_move_id.line_ids.amount_residual")
    def _compute_third_party_residual(self):
        """Computes residual amounts from Journal items."""
        for rec in self:
            rec.third_party_customer_in_state = 'pending'
            rec.third_party_customer_out_state = 'pending'
            third_party_customer_account = rec.partner_id.with_context(
                force_company=rec.company_id.id
            ).property_third_party_customer_account_id
            third_party_supplier_account = \
                rec.third_party_partner_id.with_context(
                    force_company=rec.company_id.id
                ).property_third_party_supplier_account_id
            in_residual = 0.0
            in_residual_company = 0.0
            out_residual = 0.0
            out_residual_company = 0.0
            for line in rec.sudo().third_party_move_id.line_ids:
                if line.account_id == third_party_customer_account and \
                        line.partner_id == rec.partner_id:
                    in_residual_company += line.amount_residual
                    if line.currency_id == rec.currency_id:
                        in_residual += line.amount_residual_currency if \
                            line.currency_id else line.amount_residual
                    else:
                        from_currency = (
                            (line.currency_id and line.currency_id.
                             with_context(date=line.date)) or
                            line.company_id.currency_id.
                            with_context(date=line.date))
                        in_residual += from_currency.compute(
                            line.amount_residual,
                            rec.currency_id)
                elif line.account_id == third_party_supplier_account and \
                        line.partner_id == rec.third_party_partner_id:
                    out_residual_company += line.amount_residual
                    if line.currency_id == rec.currency_id:
                        out_residual += line.amount_residual_currency if \
                            line.currency_id else line.amount_residual
                    else:
                        from_currency = (
                            (line.currency_id and line.currency_id.
                             with_context(date=line.date)) or
                            line.company_id.currency_id.
                            with_context(date=line.date))
                        out_residual += from_currency.compute(
                            line.amount_residual,
                            rec.currency_id)
            rec.third_party_customer_in_residual_company = abs(
                in_residual_company)
            rec.third_party_customer_in_residual = abs(in_residual)
            rec.third_party_customer_out_residual_company = abs(
                out_residual_company)
            rec.third_party_customer_out_residual = abs(out_residual)
            if (
                float_is_zero(
                    rec.third_party_customer_in_residual,
                    precision_rounding=rec.currency_id.rounding)
            ):
                rec.third_party_customer_in_state = 'paid'
            if (
                float_is_zero(rec.third_party_customer_out_residual,
                              precision_rounding=rec.currency_id.rounding)
            ):
                rec.third_party_customer_out_state = 'paid'

    @api.multi
    def _compute_third_party_order_count(self):
        for order in self:
            order.third_party_order_count = len(order.third_party_order_ids)

    def create_third_party_move(self):
        self.third_party_move_id = self.env['account.move'].create(
            self._third_party_move_vals())
        self.third_party_move_id.post()

    def _third_party_move_vals(self):
        journal = self.company_id.third_party_journal_id
        if not journal:
            journal = self.env['account.journal'].search([
                ('company_id', '=', self.company_id.id),
                ('type', '=', 'general')
            ], limit=1)
        third_party_customer_account = self.partner_id.with_context(
            force_company=self.company_id.id
        ).property_third_party_customer_account_id
        third_party_supplier_account = \
            self.third_party_partner_id.with_context(
                force_company=self.company_id.id
            ).property_third_party_supplier_account_id
        if not third_party_customer_account:
            raise UserError(_('Please define a third party customer account '
                              'for %s.' % self.partner_id.name))
        if not third_party_supplier_account:
            raise UserError(_('Please define a third party supplier account '
                              'for %s.' % self.third_party_partner_id.name))

        return {
            'journal_id': journal.id,
            'line_ids': [
                (0, 0, {
                    'name': self.partner_id.name,
                    'partner_id': self.partner_id.id,
                    'account_id': third_party_customer_account.id,
                    'debit': self.amount_total,
                    'credit': 0,
                }),
                (0, 0, {
                    'name': self.third_party_partner_id.name,
                    'partner_id': self.third_party_partner_id.id,
                    'account_id': third_party_supplier_account.id,
                    'debit': 0,
                    'credit': self.amount_total,
                }),
            ]
        }

    @api.model
    def _prepare_third_party_order(self):
        lines = self.order_line.filtered(lambda l: l.third_party_product_id)
        so_lines = [(0, 0, l._prepare_third_party_order_line()) for l in lines]

        return {
            'partner_id': self.third_party_partner_id.id,
            'fiscal_position_id': self.third_party_partner_id.with_context(
                force_company=self.company_id.id
            ).property_account_position_id.id or False,
            'order_line': so_lines,
            'company_id': self.company_id.id,
            'source_third_party_order_id': self.id,
        }

    @api.model
    def _create_third_party_order(self):
        vals = self._prepare_third_party_order()
        order = self.env['sale.order'].create(vals)
        order._compute_tax_id()
        return order

    @api.multi
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for order in self.filtered(lambda o: o.third_party_order):
            if not order.third_party_number and not self.env.context.get(
                'no_third_party_number', False
            ):
                sequence = order.third_party_partner_id.third_party_sequence_id
                if not sequence:
                    raise UserError(_('Please define an invoice '
                                      'sequence in the third party partner.'))
                order.third_party_number = sequence.next_by_id()
            order.create_third_party_move()
            order._create_third_party_order()
        return res

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.filtered(lambda o: o.third_party_order):
            order.action_done()
        return res

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for order in self.filtered(lambda o: o.third_party_move_id):
            order.third_party_order_ids.action_cancel()
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

    @api.constrains('third_party_order', 'third_party_partner_id')
    def _check_third_party_constrains(self):
        for rec in self:
            if rec.third_party_order and not rec.third_party_partner_id:
                raise ValidationError(
                    _('Please define a third party partner.'))

    @api.multi
    def third_party_invoice_print(self):
        return self.env.ref(
            'sale_third_party.action_report_saleorder_third_party'
        ).report_action(self)


class SalerOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('state', 'product_uom_qty', 'qty_delivered', 'qty_to_invoice',
                 'qty_invoiced', 'order_id.third_party_order')
    def _compute_invoice_status(self):
        res = super()._compute_invoice_status()
        for line in self.filtered(lambda r: r.order_id.third_party_order):
            line.invoice_status = 'no'
        return res

    third_party_price = fields.Monetary(
        currency_field='currency_id'
    )
    third_party_product_id = fields.Many2one(
        'product.product',
        domain="[('type', '=', 'service')]"
    )

    def _prepare_third_party_order_line(self):
        product = self.third_party_product_id
        return {
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            'price_unit': self.third_party_price,
        }
