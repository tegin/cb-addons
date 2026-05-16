from odoo import api, fields, models


class TOTPWizard(models.TransientModel):
    _name = "search_encounters.wizard"
    _description = "Search Encounters Wizard"

    code = fields.Char(string="Internal Identifier")

    @api.model
    def search_encounter(self, id, code):

        encounter = self.env["medical.encounter"].search(
            [("internal_identifier", "=", code)], limit=1
        )

        return {
            "id": encounter.id,
            "internal_identifier": encounter.internal_identifier,
            "commissions": [
                {
                    "name": commission.object_id.name,
                    "amount": commission.amount,
                }
                for commission in encounter.sale_order_ids.order_line.invoice_lines.agent_ids.filtered(
                    lambda r: r.agent_id.id == self.env.user.partner_id.id
                )
            ],
        }
