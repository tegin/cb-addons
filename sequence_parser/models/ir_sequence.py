from odoo import api, models
from odoo.addons.base.ir.ir_sequence import _select_nextval, _update_nogap


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.multi
    def _next_do(self):
        if self.env.context.get('sequence_tuple', False):
            if self.implementation == 'standard':
                number_next = _select_nextval(
                    self._cr, 'ir_sequence_%03d' % self.id)[0]
            else:
                number_next = _update_nogap(self, self.number_increment)
            prefix, suffix = self._get_prefix_suffix()
            return (
                prefix, number_next, suffix,
                self.get_next_char(number_next))
        return super()._next_do()


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    def _next(self):
        if self.env.context.get('sequence_tuple', False):
            if self.sequence_id.implementation == 'standard':
                number_next = _select_nextval(
                    self._cr, 'ir_sequence_%03d_%03d' % (
                        self.sequence_id.id, self.id))[0]
            else:
                number_next = _update_nogap(
                    self, self.sequence_id.number_increment)
            prefix, suffix = self.sequence_id._get_prefix_suffix()
            return (
                prefix, number_next, suffix,
                self.sequence_id.get_next_char(number_next))
        return super()._next()
