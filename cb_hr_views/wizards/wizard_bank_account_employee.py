# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.base_iban.models.res_partner_bank import validate_iban


class WizardBankAccountEmployee(models.TransientModel):

    _name = "wizard.bank.account.employee"

    name = fields.Char("_compute_name")

    acc_number = fields.Char(string="Account Number", required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee")
    bank_id = fields.Many2one("res.bank")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        if active_id:
            res["employee_id"] = self.env["hr.employee"].browse(active_id).id
        return res

    @api.multi
    def create_account(self):
        self.ensure_one()
        validate_iban(self.acc_number)
        bank_account = self.env["res.partner.bank"].create(
            {
                "acc_number": self.acc_number,
                "bank_id": self.bank_id.id,
                "partner_id": self.employee_id.partner_id.id,
                "acc_type": "iban",
            }
        )
        self.employee_id.write({"bank_account_id": bank_account.id})
        return {"type": "ir.actions.act_window_close"}
