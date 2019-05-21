# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = 'res.company'

    days_to_expire = fields.Integer(
        string="Days to set contracts to Renew",
        default="30",
        help="Is the remaining time of a contract is less "
             "than this field its state will be set to 'To renew'.",
    )
