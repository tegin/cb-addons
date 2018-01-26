
from odoo import api, models


class WizardMultiChartsAccounts(models.TransientModel):
    _inherit = 'wizard.multi.charts.accounts'

    @api.model
    def default_get(self, fields):
        res = super(WizardMultiChartsAccounts, self).default_get(fields)
        if self._context.get('company_id', False):
            res.update({
                'company_id': self._context.get('company_id')
            })
        return res
