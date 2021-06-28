# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResEncryptValue(models.TransientModel):
    _name = "res.encrypt.value"
    _inherit = "email.encryptor"
    _description = "Encrypt a mail value"

    model = fields.Char()
    res_id = fields.Integer(required=True)
    value = fields.Char(required=True)
    field = fields.Char(required=True)

    def encrypt_store(self):
        self.env[self.model].browse(self.res_id).write(
            {self.field: self._encrypt_value(self.value)}
        )
        return {}
