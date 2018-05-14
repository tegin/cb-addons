from odoo import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    default_third_party_customer_account_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False),('company_id', '=', active_id)]",
        compute='_compute_third_party_customer_account',
        inverse='_inverse_third_party_customer_account',
        string="Default Account for customers in third party sales"
    )
    default_third_party_supplier_account_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False),('company_id', '=', active_id)]",
        compute='_compute_third_party_supplier_account',
        inverse='_inverse_third_party_supplier_account',
        string="Default Account for suppliers in third party sales",
    )
    third_party_journal_id = fields.Many2one(
        'account.journal',
        domain="[('company_id', '=', active_id)]"
    )

    @api.model
    def _compute_third_party_customer_account(self):
        for rec in self:
            rec.default_third_party_customer_account_id = \
                rec.get_property_value(
                    'res.partner', 'property_third_party_customer_account_id'
                )

    @api.model
    def _inverse_third_party_customer_account(self):
        for rec in self:
            rec.set_property_value(
                'res.partner', 'property_third_party_customer_account_id',
                rec.default_third_party_customer_account_id
            )

    @api.model
    def _compute_third_party_supplier_account(self):
        for rec in self:
            rec.default_third_party_supplier_account_id = \
                rec.get_property_value(
                    'res.partner', 'property_third_party_supplier_account_id'
                )

    @api.model
    def _inverse_third_party_supplier_account(self):
        for rec in self:
            rec.set_property_value(
                'res.partner', 'property_third_party_supplier_account_id',
                rec.default_third_party_supplier_account_id
            )
