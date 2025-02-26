# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResInterCompany(models.Model):
    _name = "res.inter.company"
    _description = "res.inter.company"

    company_id = fields.Many2one(comodel_name="res.company", required=True)
    journal_id = fields.Many2one(
        comodel_name="account.journal",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    account_id = fields.Many2one(
        "account.account",
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
    inter_company_id = fields.Many2one("res.inter.company", ondelete="cascade")
    related_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Related company",
        related="inter_company_id.company_id",
        readonly=False,
        domain="[('id', '!=', company_id)]",
        required=True,
        store=True,
        index=True,
    )
    related_journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Related journal",
        related="inter_company_id.journal_id",
        readonly=False,
        domain="[('company_id', '=', related_company_id)]",
        required=True,
    )
    related_account_id = fields.Many2one(
        comodel_name="account.account",
        string="Related account",
        related="inter_company_id.account_id",
        readonly=False,
        domain="[('company_id', '=', related_company_id)]",
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ResInterCompany, self).create(vals_list)
        for res, vals in zip(records, vals_list):
            related = super(ResInterCompany, self).create(
                {
                    "company_id": vals.get("related_company_id"),
                    "journal_id": vals.get("related_journal_id"),
                    "related_company_id": vals.get("company_id"),
                    "related_journal_id": vals.get("journal_id"),
                    "account_id": vals.get("related_account_id"),
                    "related_account_id": vals.get("account_id"),
                    "inter_company_id": res.id,
                }
            )
            res.inter_company_id = related
        return records

    @api.constrains("company_id", "related_company_id")
    def _check_company(self):
        for record in self:
            if (
                self.search_count(
                    [
                        ("company_id", "=", record.company_id.id),
                        (
                            "related_company_id",
                            "=",
                            record.related_company_id.id,
                        ),
                    ]
                )
                > 1
            ):
                raise ValidationError(_("Only one record per company is allowed"))
