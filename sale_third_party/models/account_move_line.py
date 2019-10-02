from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    third_party_customer_sale_order_id = fields.Many2one(
        "sale.order", readonly=True
    )
