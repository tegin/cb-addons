# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PosSessionAddOrder(models.TransientModel):

    _name = "pos.session.add.order"
    _description = "Add Order for PoS Session"

    session_id = fields.Many2one("pos.session", required=True)
    product_id = fields.Many2one("product.product", required=True)
    fiscal_position_id = fields.Many2one("account.fiscal.position")
    partner_id = fields.Many2one("res.partner")
    price = fields.Monetary(currency_field="currency_id", required=True)
    discount = fields.Float()
    qty = fields.Integer(required=True, default=1)
    amount_total = fields.Monetary(
        currency_field="currency_id", compute="_compute_amount_total"
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="session_id.config_id.company_id.currency_id",
        readonly=True,
    )
    journal_id = fields.Many2one("account.journal", required=True)
    journal_ids = fields.Many2many(
        "account.journal",
        compute="_compute_journal_ids",
        string="Allowed Journals",
    )

    @api.depends("session_id")
    def _compute_journal_ids(self):
        for rec in self:
            rec.journal_ids = rec.session_id.statement_ids.mapped("journal_id")

    @api.onchange("product_id")
    def _onchange_product(self):
        self.price = self.product_id.lst_price

    @api.depends(
        "product_id",
        "session_id.config_id.company_id",
        "partner_id",
        "price",
        "discount",
    )
    def _compute_amount_total(self):
        for rec in self:
            taxes = rec.product_id.taxes_id.filtered(
                lambda t: t.company_id == rec.session_id.config_id.company_id
            )
            fiscal_position_id = rec.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(
                    taxes, rec.product_id, rec.partner_id
                )
            price = rec.price * (1 - (rec.discount or 0.0) / 100.0)
            taxes = taxes.compute_all(
                price,
                rec.session_id.config_id.company_id.currency_id,
                rec.qty,
                product=rec.product_id,
                partner=rec.partner_id or False,
            )
            rec.amount_total = taxes["total_included"]

    @api.multi
    def run(self):
        return self.session_id._add_manual_order(
            self.product_id,
            self.qty,
            self.price,
            self.discount,
            self.partner_id,
            self.fiscal_position_id,
            self.journal_id,
        )
