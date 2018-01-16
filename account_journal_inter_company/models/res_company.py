# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    inter_company_ids = fields.One2many(
        comodel_name='res.inter.company',
        inverse_name='company_id'
    )

    related_company_ids = fields.Many2many(
        comodel_name='res.company',
        compute='_compute_related_company_ids'
    )

    def _compute_related_company_ids(self):
        for record in self:
            record.related_company_ids = record.inter_company_ids.mapped(
                'related_company_id'
            )
