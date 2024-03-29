# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CashInvoiceOut(models.TransientModel):
    _name = "cash.third.party.sale"
    _description = "Cash Third Party Sale"
    _inherit = "cash.box.out"

    def _default_value(self, default_function):
        active_model = self.env.context.get("active_model", False)
        if active_model:
            active_ids = self.env.context.get("active_ids", False)
            return default_function(active_model, active_ids)
        return None

    def _default_company(self):
        return self._default_value(self.default_company)

    def _default_currency(self):
        return self._default_value(self.default_currency)

    def _default_journals(self):
        return self._default_value(self.default_journals)

    def _default_journal(self):
        journals = self._default_journals()
        if journals and len(journals.ids) > 0:
            return self.env["account.journal"].browse(journals.ids[0]).ensure_one()

    def _default_journal_count(self):
        return len(self._default_journals())

    sale_order_id = fields.Many2one("sale.order", string="Sale Order", required=True)
    name = fields.Char(related="sale_order_id.name", readonly=True)
    company_id = fields.Many2one(
        "res.company", default=_default_company, required=True, readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", default=_default_currency, required=True, readonly=True
    )
    journal_ids = fields.Many2many(
        "account.journal",
        default=_default_journals,
        required=True,
        readonly=True,
        string="Journals",
    )
    journal_id = fields.Many2one(
        "account.journal", required=True, default=_default_journal
    )
    journal_count = fields.Integer(default=_default_journal_count, readonly=True)

    def default_company(self, active_model, active_ids):
        return self.env[active_model].browse(active_ids)[0].company_id

    def default_currency(self, active_model, active_ids):
        return self.default_company(active_model, active_ids).currency_id

    def default_journals(self, active_model, active_ids):
        return self.env[active_model].browse(active_ids)[0].journal_id

    @api.onchange("journal_ids")
    def compute_journal_count(self):
        self.journal_count = len(self.journal_ids.ids)

    @api.onchange("journal_id")
    def _onchange_journal(self):
        self.currency_id = (
            self.journal_id.currency_id or self.journal_id.company_id.currency_id
        )

    @api.onchange("sale_order_id")
    def _onchange_sale_order(self):
        self.amount = self.sale_order_id.third_party_customer_in_residual

    def _calculate_values_for_statement_line(self, record):
        res = super()._calculate_values_for_statement_line(record)
        res["third_party_sale_order_id"] = self.sale_order_id.id
        res["counterpart_account_id"] = (
            self.sale_order_id.third_party_move_id.line_ids.filtered(
                lambda r: r.debit > 0
            )
            .mapped("account_id")
            .id
        )
        res["ref"] = self.sale_order_id.name
        res["partner_id"] = self.sale_order_id.partner_id.id
        return res
