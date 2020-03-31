# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def action_view_po(self):
        action = {
            'name': _('Purchase Order Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'target': 'current',
            'view_mode': 'tree,form',
            'domain': ['&', ('state', 'in', ['purchase', 'done']), (
                'product_id.product_tmpl_id', 'in', self.ids)],
            'context': {
                'search_default_last_year_purchase': 1,
                'search_default_status': 1,
                'search_default_order_month': 1,
            }
        }
        return action
