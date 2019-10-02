# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models
import logging
import base64

_logger = logging.getLogger(__name__)
try:
    from paramiko.client import SSHClient
except (ImportError, IOError) as err:
    _logger.info(err)


class AccountInvoiceIntegrationLog(models.Model):
    _inherit = "account.invoice.integration.log"

    def send_method(self):
        if self.integration_id.method_id == self.env.ref(
            "l10n_es_facturae_sftp.integration_sftp"
        ):
            return self.send_sftp()
        return super().send_method()

    def send_sftp(self):
        connection, sftp = self._sftp_connect()
        try:
            path = sftp.normalize(".")
            sftp.chdir(
                path + self.integration_id.invoice_id.partner_id.ssh_folder
            )
            file = sftp.open(self.integration_id.attachment_id.name, "wb")
            encoded = base64.b64decode(self.integration_id.attachment_id.datas)
            file.write(encoded)
            file.flush()
            file.close()
            if self.integration_id.attachment_ids:
                for attachment in self.integration_id.attachment_ids:
                    annex = sftp.open(attachment.name, "wb")
                    annex.write(base64.b64decode(attachment.datas))
                    annex.flush()
                    annex.close()
        except IOError as error:
            self.state = "failed"
            self.integration_id.state = "failed"
            self.log = error
            return
        self.state = "sent"
        self.integration_id.state = "sent"
        self.integration_id.can_send = False
        self.integration_id.can_cancel = False
        self.integration_id.can_update = False
        sftp.close()
        connection.close()

    def _sftp_connect(self):
        connection = SSHClient()
        connection.load_system_host_keys()
        connection.connect(
            hostname=self.integration_id.invoice_id.partner_id.ssh_server,
            port=int(self.integration_id.invoice_id.partner_id.ssh_port),
            username=self.integration_id.invoice_id.partner_id.ssh_name,
            password=self._decrypt_value(
                self.integration_id.invoice_id.partner_id.ssh_pass
            ),
        )
        sftp = connection.open_sftp()
        return connection, sftp
