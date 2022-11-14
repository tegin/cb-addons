from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    use_third_party_account = fields.Boolean(
        "Use Third Party Account",
        help="When you set this flag the payment will be recorded to "
        "the third party account defined for this partner.",
    )
    third_party_account_id = fields.Many2one(
        string="Third party account",
        comodel_name="account.account",
        readonly=True,
        compute="_compute_third_party_account_id",
    )

    @api.depends("use_third_party_account", "partner_id")
    def _compute_third_party_account_id(self):
        for rec in self:
            if rec.partner_id and rec.use_third_party_account:
                if rec.partner_type == "customer":
                    rec.third_party_account_id = rec.partner_id.with_company(
                        self.company_id.id
                    ).property_third_party_customer_account_id.id
                else:
                    rec.third_party_account_id = rec.partner_id.with_company(
                        self.company_id.id
                    ).property_third_party_supplier_account_id.id
            else:
                rec.third_party_account_id = False

    @api.depends("use_third_party_account")
    def _compute_destination_account_id(self):
        res = super()._compute_destination_account_id()
        for rec in self:
            if rec.partner_id and rec.use_third_party_account:
                rec.destination_account_id = rec.third_party_account_id
        return res
