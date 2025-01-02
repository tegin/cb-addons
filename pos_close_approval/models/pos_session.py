# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    statement_line_ids = fields.One2many(
        "account.bank.statement.line",
        inverse_name="pos_session_id",
        readonly=True,
    )
    requires_approval = fields.Boolean(related="config_id.requires_approval")

    def action_pos_session_approve(self):
        for session in self:
            balancing_account = False
            amount_to_balance = 0
            bank_payment_method_diffs = None
            if any(order.state == "draft" for order in session.order_ids):
                raise UserError(
                    _("You cannot close the POS when orders are still in draft")
                )
            if session.state == "closed":
                raise UserError(_("This session is already closed."))
            session.cash_register_balance_end_real = session.cash_register_balance_end
            session.cash_register_difference = 0.0
            session.action_pos_session_validate(
                balancing_account, amount_to_balance, bank_payment_method_diffs
            )

    def action_pos_session_closing_control(self, **kwargs):
        approved = len(self.filtered(lambda r: not r.config_id.requires_approval))
        if approved == len(self):
            return super(PosSession, self).action_pos_session_closing_control(**kwargs)
        if approved == 0:
            self.write({"rescue": True, "stop_at": fields.Datetime.now()})
            return
        raise UserError(_("Cannot close different kinds of sessions"))
