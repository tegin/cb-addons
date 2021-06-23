from odoo import models
from odoo.addons.base.models.ir_sequence import _select_nextval, _update_nogap


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _next_do(self):
        if self.env.context.get("sequence_tuple", False):
            if self.implementation == "standard":
                number_next = _select_nextval(
                    self._cr, "ir_sequence_%03d" % self.id
                )[0]
            else:
                number_next = _update_nogap(self, self.number_increment)
            prefix, suffix = self._get_prefix_suffix()
            code = self.get_next_char(number_next)
            dc = ""
            formula = self.check_digit_formula
            if formula and formula != "none":
                dc = code[-1:]
            return (prefix, number_next, suffix, dc, code)
        return super()._next_do()


class IrSequenceDateRange(models.Model):
    _inherit = "ir.sequence.date_range"

    def _next(self):
        if self.env.context.get("sequence_tuple", False):
            if self.sequence_id.implementation == "standard":
                number_next = _select_nextval(
                    self._cr,
                    "ir_sequence_%03d_%03d" % (self.sequence_id.id, self.id),
                )[0]
            else:
                number_next = _update_nogap(
                    self, self.sequence_id.number_increment
                )
            prefix, suffix = self.sequence_id._get_prefix_suffix()
            code = self.sequence_id.get_next_char(number_next)
            dc = ""
            formula = self.sequence_id.check_digit_formula
            if formula and formula != "none":
                dc = code[-1:]
            return (prefix, number_next, suffix, dc, code)
        return super()._next()
