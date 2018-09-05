from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = 'medical.request'

    cancel_reason_id = fields.Many2one('medical.cancel.reason')

    @api.constrains('state', 'cancel_reason_id')
    def check_cancel_reason_state(self):
        for rec in self:
            if rec.state == 'cancelled' and not rec.cancel_reason_id:
                raise ValidationError(_(
                    'A cancellation reason is required for cancelled requests'
                ))
            if rec.state != 'cancelled' and rec.cancel_reason_id:
                raise ValidationError(_(
                    'A cancellation reason is only allowed on cancelled '
                    'requests'
                ))

    def cancel_values(self):
        vals = super().cancel_values()
        vals.update({
            'cancel_reason_id': self.env.context.get('cancel_reason_id', False)
        })
        return vals

    def cancel(self):
        res = super().cancel()
        cancel_reason = self.env.context.get('cancel_reason', False)
        if cancel_reason:
            self.message_post(subtype=False, body=cancel_reason)
        return res
