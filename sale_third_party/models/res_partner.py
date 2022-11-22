from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    third_party_sequence_prefix = fields.Char(
        string="Prefix for Third Party Invoices",
        help="Prefix used to generate the internal reference for products "
        "created with this category. If blank the "
        "default sequence will be used.",
    )

    third_party_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Sequence for Third Party Invoices",
        readonly=True,
    )
    property_third_party_customer_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False)," "('internal_type', '=', 'receivable')]",
        company_dependent=True,
    )
    property_third_party_supplier_account_id = fields.Many2one(
        "account.account",
        domain="[('deprecated', '=', False)," "('internal_type', '=', 'payable')]",
        company_dependent=True,
    )

    @api.model
    def _prepare_ir_sequence(self, prefix):
        """Prepare the vals for creating the sequence
        :param prefix: a string with the prefix of the sequence.
        :return: a dict with the values.
        """
        vals = {
            "name": "Partner " + prefix,
            "code": "third.party.partner.invoice - " + prefix,
            "padding": 5,
            "prefix": prefix,
            "company_id": False,
            "implementation": "no_gap",
        }
        return vals

    def write(self, vals):
        prefix = vals.get("third_party_sequence_prefix")
        if prefix:
            for rec in self:
                if rec.third_party_sequence_id:
                    rec.sudo().third_party_sequence_id.prefix = prefix
                else:
                    seq_vals = self._prepare_ir_sequence(prefix)
                    rec.third_party_sequence_id = (
                        self.env["ir.sequence"].sudo().create(seq_vals)
                    )
        return super().write(vals)

    @api.model
    def create(self, vals):
        prefix = vals.get("third_party_sequence_prefix")
        if prefix:
            seq_vals = self._prepare_ir_sequence(prefix)
            sequence = self.env["ir.sequence"].create(seq_vals)
            vals["third_party_sequence_id"] = sequence.id
        return super().create(vals)
