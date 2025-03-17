import logging
import os

from odoo import api, models
from odoo.tools.config import config

_logger = logging.getLogger(__name__)
try:
    from cryptography.fernet import Fernet
except ImportError as err:
    _logger.debug(err)


class EmailEncryptor(models.AbstractModel):
    _name = "email.encryptor"
    _description = "email.encryptor"

    def _get_cipher_key(self):
        if os.getenv("EMAIL_INTEGRATION_CIPHER_KEY"):
            return os.getenv("EMAIL_INTEGRATION_CIPHER_KEY")
        return config.get("email_integration_key")

    @api.model
    def _get_chipher(self):
        return Fernet(self._get_cipher_key())

    @api.model
    def _encrypt_value(self, value):
        return self._get_chipher().encrypt(value.encode())

    @api.model
    def _decrypt_value(self, value):
        return self._get_chipher().decrypt(value.encode())
