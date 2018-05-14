from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    third_party_sequence_id = fields.Many2one(
        'ir.sequence',
    )
    property_third_party_customer_account_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False)]",
        company_dependent=True,
    )
    property_third_party_supplier_account_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False)]",
        company_dependent=True,
    )


class PartnerProperty(models.TransientModel):
    _inherit = 'res.partner.property'

    property_third_party_customer_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account for customers in third party sales",
        domain="[('deprecated', '=', False),"
               "('company_id', '=', company_id)]",
        compute='_compute_property_fields',
        readonly=False, store=False,
    )
    property_third_party_supplier_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account for suppliers in third party sales",
        domain="[('deprecated', '=', False),"
               "('company_id', '=', company_id)]",
        compute='_compute_property_fields',
        readonly=False, store=False,
    )

    @api.multi
    def get_property_fields(self, object, properties):
        super(PartnerProperty, self).get_property_fields(object, properties)
        for rec in self:
            rec.property_third_party_customer_account_id = \
                rec.get_property_value(
                    'property_third_party_customer_account_id',
                    object, properties)
            rec.property_third_party_supplier_account_id = \
                rec.get_property_value(
                    'property_third_party_supplier_account_id',
                    object, properties)

    @api.multi
    def get_property_fields_list(self):
        res = super(PartnerProperty, self).get_property_fields_list()
        res.append('property_third_party_customer_account_id')
        res.append('property_third_party_supplier_account_id')
        return res
