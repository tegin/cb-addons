# Copyright 2025 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ChangePaymentMethodWizard(models.TransientModel):

    _name = "change.payment.method.wizard"
    _description = "Wizard para cambiar método de pago"

    payment_id = fields.Many2one("pos.payment", required=True, readonly=True)
    old_payment_method_id = fields.Many2one(
        "pos.payment.method",
        string="Método de pago antiguo",
        required=True,
        readonly=True,
    )
    new_payment_method_id = fields.Many2one(
        "pos.payment.method", string="Nuevo método de pago", required=True
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get("active_id")
        if active_id:
            payment = self.env["pos.payment"].browse(active_id)
            res.update(
                {
                    "payment_id": payment.id,
                    "old_payment_method_id": payment.payment_method_id.id,
                }
            )
        return res

    def confirm_change(self):
        self.ensure_one()
        payment = self.payment_id
        session = payment.pos_order_id.session_id
        if session.state == "closed":
            raise UserError(
                _("The session is closed, the payment method cannot be changed.")
            )
        payment.payment_method_id = self.new_payment_method_id
