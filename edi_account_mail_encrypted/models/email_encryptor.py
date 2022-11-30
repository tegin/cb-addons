import logging

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

    @api.model
    def _get_chipher(self):
        return Fernet(config.get("email_integration_key"))

    @api.model
    def _encrypt_value(self, value):
        return self._get_chipher().encrypt(value.encode())

    @api.model
    def _decrypt_value(self, value):
        return self._get_chipher().decrypt(value.encode())
