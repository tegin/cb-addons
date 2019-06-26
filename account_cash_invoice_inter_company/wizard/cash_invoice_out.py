# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CashInvoiceOut(models.TransientModel):
    _inherit = 'cash.invoice.out'

    inter_company_ids = fields.Many2many(
        'res.company',
        related='company_id.related_company_ids',
        readonly=True,
    )
