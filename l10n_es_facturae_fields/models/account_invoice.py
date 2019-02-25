# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.addons.base_sparse_field.models.fields import Serialized


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    facturae_fields = Serialized()
    receiver_contract_reference = fields.Char(
        sparse="facturae_fields"
    )
    receiver_contract_date = fields.Date(
        sparse="facturae_fields"
    )
    receiver_transaction_reference = fields.Char(
        sparse="facturae_fields"
    )
    receiver_transaction_date = fields.Date(
        sparse="facturae_fields"
    )
    issuer_contract_reference = fields.Char(
        sparse="facturae_fields"
    )
    issuer_contract_date = fields.Date(
        sparse="facturae_fields"
    )
    issuer_transaction_reference = fields.Char(
        sparse="facturae_fields"
    )
    issuer_transaction_date = fields.Date(
        sparse="facturae_fields"
    )
    file_reference = fields.Char(
        sparse="facturae_fields"
    )
    file_date = fields.Date(
        sparse="facturae_fields"
    )
