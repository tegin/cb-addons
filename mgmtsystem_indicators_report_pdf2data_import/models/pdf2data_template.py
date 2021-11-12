# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Pdf2dataTemplate(models.Model):

    _inherit = "pdf2data.template"

    mgmtsystem_indicator_template_id = fields.Many2one(
        "mgmtsystem.indicators.report.template"
    )
