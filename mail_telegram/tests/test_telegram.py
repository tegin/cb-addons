import mock
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tests.common import SavepointCase
from odoo.tools import file_open, mute_logger


class TestTelegram(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.body = "MY MESSAGE"
        cls.bot = cls.env["mail.telegram.bot"].create(
            {"name": "BOT", "token": "TOKEN"}
        )
        cls.chat = cls.env["mail.telegram.chat"].create(
            {"bot_id": cls.bot.id, "name": "CHAT", "chat_id": "1234"}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "My Demo Partner"}
        )
        cls.message_id = 1

    def _send_telegram_message(self, telegram):
        parent_self = self

        class MockMessage:
            def __init__(self):
                self.message_id = parent_self.message_id
                parent_self.message_id += 1

        class MockChat:
            def __init__(self, chat_id):
                pass

            def send_message(self, data, parse_mode=False):
                return MockMessage()

            def send_photo(self, data):
                return MockMessage()

            def send_document(self, data, filename=False):
                return MockMessage()

        class MockBot:
            def __init__(self, bot_id):
                pass

            def get_chat(self, chat_id=False):
                return MockChat(chat_id)

        with mock.patch(
            "odoo.addons.mail_telegram.models.mail_message_telegram.Bot"
        ) as patch:
            patch.return_value = MockBot
            telegram.send()
            patch.assert_called_once()

    def test_telegram(self):
        message = self.partner.message_post(
            body=self.body,
            message_type="telegram",
            subtype=self.env.ref("mail_telegram.mt_telegram"),
        )
        message_format = message.message_format()[0]
        self.assertFalse(message_format["telegram"])
        telegram_message = self.env["mail.message.telegram"].create(
            {"mail_message_id": message.id, "chat_id": self.chat.id}
        )
        self._send_telegram_message(telegram_message)
        self.assertEqual(telegram_message.state, "sent")
        self.assertTrue(telegram_message.message_id)
        message.refresh()
        message_format = message.message_format()[0]
        self.assertTrue(message_format["telegram"])
        self.assertEqual(message_format["customer_telegram_status"], "sent")

    def test_telegram_attachment(self):
        message = self.partner.message_post(
            body=self.body,
            message_type="telegram",
            subtype=self.env.ref("mail_telegram.mt_telegram"),
            attachments=[("file.txt", "FILE DATA")],
        )
        message.flush()
        self.assertTrue(message.attachment_ids)
        telegram_message = self.env["mail.message.telegram"].create(
            {"mail_message_id": message.id, "chat_id": self.chat.id}
        )
        self._send_telegram_message(telegram_message)
        self.assertEqual(telegram_message.state, "sent")
        self.assertTrue(telegram_message.message_id)

    def test_telegram_attachment_image(self):
        image = file_open(
            "icon.png",
            mode="rb",
            subdir="addons/mail_telegram/static/description",
        ).read()
        message = self.partner.message_post(
            body=self.body,
            message_type="telegram",
            subtype=self.env.ref("mail_telegram.mt_telegram"),
            attachments=[("file.png", image)],
        )
        message.body = False
        self.assertTrue(message.attachment_ids)
        telegram_message = self.env["mail.message.telegram"].create(
            {"mail_message_id": message.id, "chat_id": self.chat.id}
        )
        self._send_telegram_message(telegram_message)
        self.assertEqual(telegram_message.state, "sent")
        self.assertTrue(telegram_message.message_id)

    @mute_logger("odoo.addons.mail_telegram.models.mail_message_telegram")
    def test_exception(self):
        message = self.partner.message_post(
            body=self.body,
            message_type="telegram",
            subtype=self.env.ref("mail_telegram.mt_telegram"),
        )
        telegram_message = self.env["mail.message.telegram"].create(
            {"mail_message_id": message.id, "chat_id": self.chat.id}
        )
        telegram_message.send()
        self.assertTrue(telegram_message.failure_reason)
        self.assertEqual(telegram_message.state, "exception")
        telegram_message.mark_outgoing()
        self.assertEqual(telegram_message.state, "outgoing")
        telegram_message.cancel()
        self.assertEqual(telegram_message.state, "cancel")

    @mute_logger("odoo.addons.mail_telegram.models.mail_message_telegram")
    def test_raises(self):
        message = self.partner.message_post(
            body=self.body,
            message_type="telegram",
            subtype=self.env.ref("mail_telegram.mt_telegram"),
        )
        telegram_message = self.env["mail.message.telegram"].create(
            {"mail_message_id": message.id, "chat_id": self.chat.id}
        )
        with self.assertRaises(MailDeliveryException):
            telegram_message.send(raise_exception=True)
