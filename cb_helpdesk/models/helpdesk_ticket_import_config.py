# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HelpdeskTicketImportConfig(models.Model):

    _name = "helpdesk.ticket.import.config"
    _description = "Configuration Line for Ticket importing"  # TODO

    name = fields.Char(required=True)
    start_row = fields.Integer(default=2)
    start_col = fields.Integer(default=1)
    line_ids = fields.One2many(
        "helpdesk.ticket.import.config.line", copy=True, inverse_name="configuration_id"
    )
    report_id = fields.Many2one(
        "ir.actions.report", domain=[("model", "=", "helpdesk.ticket.import")]
    )
    description = fields.Html()


class HelpdeskTicketImportConfigLine(models.Model):
    _name = "helpdesk.ticket.import.config.line"
    _description = "Configuration Line for ticket importing"
    _order = "sequence, id"

    configuration_id = fields.Many2one(
        "helpdesk.ticket.import.config", required=True, ondelete="cascade"
    )
    col = fields.Integer(required=True)
    name = fields.Char(required=True)
    kind = fields.Selection(
        [
            ("string", "String"),
            ("float", "Float"),
            ("date", "Date"),
            ("datetime", "Datetime"),
        ],
        required=True,
        default="string",
    )
    sequence = fields.Integer(default=20)

    def _import_data(self, sheet, line):
        value = sheet.cell(line, self.col).value
        if value is None:
            return False
        if hasattr(self, "_import_data_%s" % self.kind):
            return getattr(self, "_import_data_%s" % self.kind)(value)
        return value
