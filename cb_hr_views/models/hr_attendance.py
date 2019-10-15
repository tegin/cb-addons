# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    center_id = fields.Many2one(
        string="Center",
        related="employee_id.address_id",
        comodel_name="res.partner",
        readonly=True,
        store=True,
    )
