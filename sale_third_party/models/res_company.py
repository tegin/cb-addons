from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_third_party_customer_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False),"
        "('company_id', '=', active_id),"
        "('internal_type', '=', 'receivable')]",
        compute="_compute_third_party_customer_account",
        inverse="_inverse_third_party_customer_account",
        string="Default Account for customers in third party sales",
    )
    default_third_party_supplier_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False),"
        "('company_id', '=', active_id),"
        "('internal_type', '=', 'payable')]",
        compute="_compute_third_party_supplier_account",
        inverse="_inverse_third_party_supplier_account",
        string="Default Account for suppliers in third party sales",
    )
    third_party_journal_id = fields.Many2one(
        "account.journal", domain="[('company_id', '=', active_id)]"
    )

    def get_property_value(self, model, field):
        value = self.env["ir.property"].with_company(self).sudo()._get(field, model)
        if value:
            if isinstance(value, list):
                return value[0]
            else:
                return value
        return False

    def set_property_value(self, model, field_name, value):
        field = (
            self.env["ir.model.fields"]
            .sudo()
            .search([("name", "=", field_name), ("model", "=", model)], limit=1)
        )
        if isinstance(value, models.BaseModel):
            if value:
                val = value.id
            else:
                val = False
        else:
            val = value
        prop = (
            self.env["ir.property"]
            .sudo()
            .search(
                [
                    ("name", "=", field_name),
                    ("fields_id", "=", field.id),
                    ("company_id", "=", self.id),
                    ("res_id", "=", False),
                ]
            )
        )
        if not prop:
            prop = (
                self.env["ir.property"]
                .sudo()
                .create(
                    {
                        "name": field_name,
                        "fields_id": field.id,
                        "company_id": self.id,
                        "res_id": False,
                    }
                )
            )
        if isinstance(value, models.BaseModel) and not val:
            prop.sudo().unlink()
        else:
            prop.sudo().write({"value": val})

    @api.model
    def _compute_third_party_customer_account(self):
        for rec in self:
            rec.default_third_party_customer_account_id = rec.get_property_value(
                "res.partner", "property_third_party_customer_account_id"
            )

    @api.model
    def _inverse_third_party_customer_account(self):
        for rec in self:
            rec.set_property_value(
                "res.partner",
                "property_third_party_customer_account_id",
                rec.default_third_party_customer_account_id,
            )

    @api.model
    def _compute_third_party_supplier_account(self):
        for rec in self:
            rec.default_third_party_supplier_account_id = rec.get_property_value(
                "res.partner", "property_third_party_supplier_account_id"
            )

    @api.model
    def _inverse_third_party_supplier_account(self):
        for rec in self:
            rec.set_property_value(
                "res.partner",
                "property_third_party_supplier_account_id",
                rec.default_third_party_supplier_account_id,
            )
