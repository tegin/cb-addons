from odoo import api, models
from odoo.tools.config import config
import logging
_logger = logging.getLogger(__name__)
try:
    from cryptography.fernet import Fernet
except ImportError as err:
    _logger.debug(err)


class EmailEncryptor(models.AbstractModel):
    _name = 'email.encryptor'

    @api.model
    def _get_chipher(self):
        return Fernet(config.get('email_integration_key'))

    @api.model
    def _encrypt_value(self, value):
        cipher = self._get_chipher()
        _logger.info(cipher)
        return self._get_chipher().encrypt(value.encode())

    @api.model
    def _decrypt_value(self, value):
        return self._get_chipher().decrypt(value.encode())
