# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    ssh_server = fields.Char(string="SSH Server")
    ssh_port = fields.Char(string="SSH Port", default=22)
    ssh_name = fields.Char(string="SSH Name")
    ssh_pass = fields.Char(string="SSH Password", readonly=True)
    ssh_folder = fields.Char(string="SSH Folder")
    ssh_report_id = fields.Many2one(
        "ir.actions.report",
        domain=[("model", "=", "account.invoice")],
        string="SSH Report",
    )

    @api.constrains(
        "ssh_server",
        "ssh_port",
        "ssh_name",
        "ssh_pass",
        "ssh_folder",
        "ssh_report_id",
        "invoice_integration_method_ids",
    )
    def sftp_parameters_constrains(self):
        if (
            self.env.ref("l10n_es_facturae_sftp.integration_sftp")
            in self.invoice_integration_method_ids
        ):
            if not (
                self.ssh_server
                and self.ssh_port
                and self.ssh_name
                and self.ssh_pass
                and self.ssh_folder
                and self.ssh_report_id
            ):
                raise ValidationError(
                    _(
                        "You need to configure the SSH Server, SSH Port, SSH Name"
                        "SSH Password, SSH Folder and the SSH Report if you want"
                        "to use SFTP integration method"
                    )
                )
