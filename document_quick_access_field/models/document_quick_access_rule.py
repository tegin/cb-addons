# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re


class DocumentQuickAccessRule(models.Model):
    _inherit = 'document.quick.access.rule'

    barcode_format = fields.Selection(selection_add=[
        ('field', 'Field')
    ])
    field_name = fields.Char()
    field_format = fields.Char()

    @api.constrains('barcode_format', 'field_name')
    def _check_field_barcode_format(self):
        for record in self:
            if record.barcode_format == 'field':
                if not record.field_name:
                    raise ValidationError(_('Field name is required'))

    def _get_code_field(self, record):
        return getattr(record, self.field_name)

    def _check_code_field(self, code):
        for rule in self.search([('barcode_format', '=', 'field')]):
            if re.match(rule.field_format, code):
                return True
        return False

    def _read_code_field(self, code):
        for rule in self.search([('barcode_format', '=', 'field')]):
            if not rule.field_format or re.match(rule.field_format, code):
                record = self.env[rule.model_id.model].search([
                    (rule.field_name, '=', code)
                ]).exists()
                if record:
                    return record
        return self
