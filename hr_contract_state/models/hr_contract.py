# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('renewed', 'Renewed'),
        ('to_expire', 'To Expire'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], readonly=True, copy=False)

    renewed_contract_id = fields.Many2one(
        'hr.contract',
        string='Renewed Contract',
        readonly=True,
        copy=False
    )
    date_end = fields.Date(copy=False)

    company_id = fields.Many2one(required=True)

    @api.model
    def update_state(self, identifier=False):
        if self.env.context.get('execute_old_update', False):
            return super().update_state()
        id_domain = []
        if identifier:
            id_domain = [('id', '=', identifier)]
        today = fields.Date.today()
        self.search([
            ('state', '=', 'draft'),
            ('date_start', '<=', today),
        ] + id_domain).write({'state': 'open'})
        for company in self.env['res.company'].search([]):
            self.search([
                ('company_id', '=', company.id),
                ('state', '=', 'open'),
                ('date_end', '!=', False),
                ('date_end', '<=', fields.Date.to_string(
                    fields.Date.from_string(today) +
                    timedelta(days=company.days_to_expire)
                )),
            ] + id_domain).write({'state': 'pending'})
        self.search([
            ('state', 'in', ['renewed', 'to_expire', 'pending']),
            ('date_end', '<', today),
        ] + id_domain).write({'state': 'close'})
        return True

    @api.multi
    def pending2to_expire(self):
        for record in self:
            record.write({'state': 'to_expire'})

    @api.multi
    def renew_contract(self):
        self.ensure_one()
        date_end = self.date_end or fields.Date.today()
        next_day = fields.Date.to_string(
            fields.Date.from_string(date_end) + timedelta(days=1)
        )
        new_contract = self.copy({
            'date_start': next_day
        })
        self.write({
            'state': 'renewed',
            'renewed_contract_id': new_contract.id,
        })
        action = self.env.ref('hr_contract.action_hr_contract')
        result = action.read()[0]
        result['res_id'] = new_contract.id
        result['views'] = [(False, 'form')]
        return result

    @api.model
    def create(self, vals):
        res = super().create(vals)
        self.update_state(res.id)
        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if ('date_start' in vals) or ('date_end' in vals):
            for record in self:
                self.update_state(record.id)
        return res
