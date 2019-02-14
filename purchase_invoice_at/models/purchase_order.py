# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.addons.purchase.models.purchase import PurchaseOrder as PO


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_to_invoice_id = fields.Many2one(
        'res.partner', 'Partner to invoice',
        states=PO.READONLY_STATES,
        ondelete='restrict',
    )

    @api.constrains('company_id', 'partner_to_invoice_id')
    def _check_company_partner_to_invoice(self):
        """
        The company of the partner to invoice must be consistent with the
        company of the purchase order
        """
        for record in self:
            partner = record.partner_to_invoice_id
            if partner.company_id and partner.company_id != record.company_id:
                raise models.ValidationError(_(
                    'Partner to invoice must belong to the same company'))

    @api.onchange('company_id')
    def _onchange_company_partner_to_invoice(self):
        for record in self:
            partner = record.partner_to_invoice_id
            if (
                partner and partner.company_id and
                partner.company_id != record.company_id
            ):
                record.partner_to_invoice_id = False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('invoice_lines.invoice_id.state', 'invoice_lines.quantity',
                 'invoice_lines.uom_id', 'qty_received',
                 'order_id.partner_to_invoice_id',
                 )
    def _compute_qty_invoiced(self):
        """
        No quantity should be invoices if the partner_to_invoice is selected
        """
        super()._compute_qty_invoiced()
        for record in self.filtered(
                lambda r: r.order_id.partner_to_invoice_id):
            record.qty_invoiced = record.qty_received
