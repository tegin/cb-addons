# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    account_integration_report_id = fields.Many2one(
        "ir.actions.report",
        domain=[("model", "=", "account.invoice")],
        string="Account Integration Report",
    )  # What do we send?
    account_integration_storage_id = fields.Many2one(
        "storage.backend"
    )  # How do we send it?
    account_integration_filename_pattern = fields.Char()  # How do we name it?

    @api.constrains(
        "account_integration_report_id",
        "invoice_integration_method_ids",
        "account_integration_storage_id",
        "account_integration_filename_pattern",
    )
    def _check_account_integration_storage_parameters(self):
        if (
            self.env.ref("l10n_es_facturae_storage.integration_storage")
            in self.invoice_integration_method_ids
        ):
            if not self.account_integration_report_id:
                raise ValidationError(
                    _(
                        "You need to configure"
                        "the Account Integration Report if you want"
                        "to use Storage integration method"
                    )
                )
            if not self.account_integration_storage_id:
                raise ValidationError(
                    _(
                        "You need to configure "
                        "the Account Integration Storage if you want"
                        "to use Storage integration method"
                    )
                )
            if not self.account_integration_filename_pattern:
                raise ValidationError(
                    _(
                        "You need to configure "
                        "the Account Integration Filename Pattern if you want"
                        "to use Storage integration method"
                    )
                )
