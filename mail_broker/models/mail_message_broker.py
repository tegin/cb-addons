# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
import traceback
from io import BytesIO, StringIO

from odoo import _, api, fields, models
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tools import html2plaintext
from telegram import Bot

_logger = logging.getLogger(__name__)


class MailMessageBroker(models.Model):
    _name = "mail.message.broker"
    _description = "Broker Message"
    _inherits = {"mail.message": "mail_message_id"}
    _order = "id desc"
    _rec_name = "subject"

    # content
    mail_message_id = fields.Many2one(
        "mail.message",
        "Mail Message",
        required=True,
        ondelete="cascade",
        index=True,
        auto_join=True,
    )
    message_id = fields.Char(readonly=True)
    channel_id = fields.Many2one(
        "mail.broker.channel", required=True, ondelete="cascade"
    )
    state = fields.Selection(
        [
            ("outgoing", "Outgoing"),
            ("sent", "Sent"),
            ("exception", "Delivery Failed"),
            ("cancel", "Cancelled"),
            ("received", "Received"),
        ],
        "Status",
        readonly=True,
        copy=False,
        default="outgoing",
    )
    failure_reason = fields.Text(
        "Failure Reason",
        readonly=1,
        help="Failure reason. This is usually the exception thrown by the"
        " email server, stored to ease the debugging of mailing issues.",
    )

    # TODO: ALSO Pass it to mail_broker_telegram ????
    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)
        if self.env.context.get("notify_broker", False):
            notifications = []
            for message in messages:
                notifications.append(
                    [
                        (
                            self._cr.dbname,
                            "mail.broker",
                            message.channel_id.broker_id.id,
                        ),
                        {
                            "message": message.mail_message_id.message_format()[
                                0
                            ]
                        },
                    ]
                )
            self.env["bus.bus"].sendmany(notifications)
        return messages

    def send(
        self, auto_commit=False, raise_exception=False, parse_mode="HTML"
    ):
        for record in self:
            getattr(
                record, "_send_%s" % record.channel_id.broker_id.broker_type
            )(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                parse_mode=parse_mode,
            )

    # TODO: Pass it to mail_broker_telegram
    def _send_telegram(
        self, auto_commit=False, raise_exception=False, parse_mode=False
    ):
        message = False
        try:
            bot = Bot(self.channel_id.broker_token)
            chat = bot.get_chat(self.channel_id.token)
            if self.body:
                message = chat.send_message(
                    html2plaintext(self.body), parse_mode=parse_mode
                )
            for attachment in self.attachment_ids:
                if attachment.mimetype.split("/")[0] == "image":
                    new_message = chat.send_photo(
                        BytesIO(base64.b64decode(attachment.datas))
                    )
                else:
                    new_message = chat.send_document(
                        BytesIO(base64.b64decode(attachment.datas)),
                        filename=attachment.name,
                    )
                if not message:
                    message = new_message
        except Exception as exc:
            buff = StringIO()
            traceback.print_exc(file=buff)
            _logger.error(buff.getvalue())
            if raise_exception:
                raise MailDeliveryException(
                    _("Unable to send the telegram message"), exc
                )
            else:
                _logger.warning(
                    "Issue sending message with id {}: {}".format(self.id, exc)
                )
                self.write({"state": "exception", "failure_reason": exc})
        if message:
            self.write(
                {
                    "state": "sent",
                    "message_id": message.message_id,
                    "failure_reason": False,
                }
            )
        if auto_commit is True:
            # pylint: disable=invalid-commit
            self._cr.commit()

    def mark_outgoing(self):
        return self.write({"state": "outgoing"})

    def cancel(self):
        return self.write({"state": "cancel"})
