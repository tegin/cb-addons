# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import zipfile
from collections import defaultdict
from io import BytesIO

import openpyxl

from odoo import SUPERUSER_ID, _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.delay import group


class HelpdeskTicketImport(models.Model):
    _name = "helpdesk.ticket.import"
    _inherit = "mail.thread"
    _description = "Import File"

    name = fields.Char(
        required=True, readonly=True, states={"draft": [("readonly", False)]}
    )
    data = fields.Binary(
        attachment=True, readonly=True, states={"draft": [("readonly", False)]}
    )
    filename = fields.Char(readonly=True, states={"draft": [("readonly", False)]})
    team_id = fields.Many2one("helpdesk.ticket.team")
    configuration_id = fields.Many2one(
        "helpdesk.ticket.import.config",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported")],
        copy=False,
        default="draft",
        readonly=True,
    )
    ticket_ids = fields.One2many("helpdesk.ticket", inverse_name="helpdesk_import_id")
    file_ids = fields.One2many(
        "helpdesk.ticket.import.file", inverse_name="helpdesk_import_id"
    )
    generate_files = fields.Boolean(default=True)
    generate_tickets = fields.Boolean(default=True)

    def import_data(self):
        self.ensure_one()
        if self.state != "draft":
            raise ValidationError(_("You can only import files in draft state"))
        if not self.team_id and self.generate_tickets:
            raise ValidationError(_("Team is required"))
        self.state = "imported"
        line = self.configuration_id.start_row
        workbook = openpyxl.load_workbook(BytesIO(base64.b64decode(self.data)))
        sheet = workbook.active
        data = []
        while True:
            if sheet.cell(line, self.configuration_id.start_col).value is None:
                break
            data.append(self._import_data(sheet, line))
            line += 1
        filenames = defaultdict(lambda: 0)
        jobs = []
        for import_data in data:
            filenames[import_data.get("name", "")] += 1
            import_data["filename"] = "%s_%s.pdf" % (
                import_data.get("name", ""),
                filenames[import_data.get("name", "")],
            )
            jobs.append(self.delayable()._generate_record(import_data))
        group(*jobs).on_done(self.delayable().generate_full_file()).delay()

    def generate_full_file(self):
        if not self.generate_files:
            return
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for attachment in self.file_ids:
                zip_file.writestr(
                    attachment.filename,
                    base64.b64decode(attachment.datas),
                )
            zip_buffer.seek(0)
            zip_file.close()
        self.with_user(SUPERUSER_ID).message_post(
            body=_("File has been generated"),
            attachments=[("full.zip", zip_buffer.getvalue())],
            subtype_id=self.env.ref("mail.mt_comment").id,
        )

    def _generate_record(self, import_data):
        if self.generate_files:
            renderized_data = self.configuration_id.report_id._render(
                self.ids, data=import_data
            )
            self.env["helpdesk.ticket.import.file"].create(
                {
                    "filename": import_data["filename"],
                    "helpdesk_import_id": self.id,
                    "datas": base64.b64encode(renderized_data[0]),
                }
            )
        if self.generate_tickets:
            self.env["helpdesk.ticket"].create(self._helpdesk_ticket_vals(import_data))

    def _helpdesk_ticket_vals(self, import_data):
        return {
            "helpdesk_import_id": self.id,
            "name": import_data["name"],
            "team_id": self.team_id.id,
            "partner_name": import_data["name"],
            "partner_email": import_data.get("email", False),
            "partner_phone": import_data.get("phone", False),
            "description": import_data.get(
                "description", self.configuration_id.description
            ),
        }

    def _import_data(self, sheet, line):
        result = defaultdict(lambda: [])
        for configuration_line in self.configuration_id.line_ids:
            value = configuration_line._import_data(sheet, line)
            result.setdefault(configuration_line.name, [])
            if value:
                result[configuration_line.name].append(value)
        return {key: " ".join(result[key]) for key in result}


class HelpdeskTicketImportFile(models.Model):
    _name = "helpdesk.ticket.import.file"
    _description = "Import Helpdesk tickets files"
    helpdesk_import_id = fields.Many2one("helpdesk.ticket.import", required=True)
    datas = fields.Binary()
    filename = fields.Char()
