# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResEncryptValue(models.TransientModel):
    _name = 'res.encrypt.value'
    _inherit = 'email.encryptor'

    model = fields.Char()
    res_id = fields.Integer(
        required=True
    )
    value = fields.Char(required=True)
    field = fields.Char(required=True)

    @api.multi
    def doit(self):
        self.env[self.model].browse(self.res_id).write({
            self.field: self._encrypt_value(self.value)
        })
        return {}
