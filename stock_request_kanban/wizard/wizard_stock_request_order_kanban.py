# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from reportlab.graphics.barcode import getCodes


class WizardStockRequestOrderKanban(models.TransientModel):
    _name = "wizard.stock.request.order.kanban"
    _inherit = "barcodes.barcode_events_mixin"

    order_id = fields.Many2one(
        'stock.request.order',
        required=True
    )
    kanban_id = fields.Many2one(
        'stock.request.kanban',
        readonly=True,
    )
    stock_request_id = fields.Many2one(
        'stock.request',
        readonly=True,
    )
    status = fields.Text(
        readonly=True,
        default="Start scanning",
    )
    status_state = fields.Integer(
        default=0,
        readonly=True,
    )

    def get_barcode_format(self):
        return 'Standard39'

    def validate_barcode(self, barcode):
        bcc = getCodes()[self.get_barcode_format()](value=barcode[:-1])
        bcc.validate()
        bcc.encode()
        if bcc.encoded[1:-1] != barcode:
            raise ValidationError(_('CRC is not valid'))
        return barcode[:-1]

    def on_barcode_scanned(self, barcode):
        barcode = self.validate_barcode(barcode)

        self.kanban_id = self.env['stock.request.kanban'].search([
            ('name', '=', barcode)
        ])
        if not self.kanban_id:
            self.status = _("Barcode %s does not correspond to any "
                            "Kanban. Try with another barcode or "
                            "press Close to finish scanning.") % barcode
            self.status_state = 1
            return
        if self.order_id.stock_request_ids.filtered(
            lambda r: r.kanban_id == self.kanban_id
        ):
            self.status = _("Barcode %s is on the order") % barcode
            self.status_state = 1
            return
        self.validate_kanban()

        self.stock_request_id = self.env['stock.request'].create(
            self.stock_request_kanban_values()
        )
        self.order_id = self.stock_request_id.order_id
        self.status_state = 0

        self.status = _('Added kanban %s for product %s' % (
            self.stock_request_id.kanban_id.name,
            self.stock_request_id.product_id.display_name
        ))
        return

    def validate_kanban(self):
        if self.order_id.state != 'draft':
            raise ValidationError(_(
                'Lines only can be added on orders with draft state'))
        if not self.order_id.company_id:
            self.order_id.company_id = self.kanban_id.company_id
        elif self.order_id.company_id != self.kanban_id.company_id:
            raise ValidationError(_('Company must be the same'))
        if (
            self.kanban_id.procurement_group_id and
            self.order_id.procurement_group_id !=
                self.kanban_id.procurement_group_id
        ):
            raise ValidationError(_('Procurement group must be the same'))
        if self.order_id.location_id != self.kanban_id.location_id:
            raise ValidationError(_('Location must be the same'))
        if self.order_id.warehouse_id != self.kanban_id.warehouse_id:
            raise ValidationError(_('Warehouse must be the same'))

    def stock_request_kanban_values(self):
        return {
            'order_id': self.order_id.id,
            'company_id': self.order_id.company_id.id,
            'procurement_group_id':
                self.order_id.procurement_group_id.id or False,
            'location_id': self.order_id.location_id.id or False,
            'warehouse_id': self.order_id.warehouse_id.id or False,
            'expected_date': self.order_id.expected_date or False,
            'picking_policy': self.order_id.picking_policy or False,
            'requested_by': self.order_id.requested_by.id,
            'product_id': self.kanban_id.product_id.id,
            'product_uom_id': self.kanban_id.product_uom_id.id or False,
            'route_id': self.kanban_id.route_id.id or False,
            'product_uom_qty': self.kanban_id.product_uom_qty,
            'kanban_id': self.kanban_id.id,
        }
