# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailMail(models.Model):

    _inherit = "mail.mail"

    def _postprocess_sent_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        msg = self.mail_message_id
        if msg.model == "credit.control.communication":
            mt_request = self.env.ref("account_credit_control.mt_request")
            if self.subtype_id == mt_request:
                self.env[msg.model].browse(msg.res_id).write(
                    {
                        "state": "sent"
                        if self.state == "sent"
                        else "email_error",
                    }
                )
        return super()._postprocess_sent_message(
            success_pids,
            failure_reason=failure_reason,
            failure_type=failure_type,
        )
