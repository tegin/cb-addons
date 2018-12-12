# -*- coding: utf-8 -*-
# Copyright (C) 2017 Creu Blanca
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.modules.registry import Registry


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    safe = fields.Boolean(
        default=False,
        help="When safe is checked, it is opening a new cursor in order to "
             "create the number. This way, we ensure the unicity of the code."
    )

    def _next(self):
        if self.env.context.get('ignore_safe', not self.safe):
            return super()._next()
        new_cr = Registry(self.env.cr.dbname).cursor()
        try:
            env = api.Environment(new_cr, self.env.uid, self.env.context)
            res = env[self._name].browse(self.id)
            result = res.with_context(ignore_safe=True)._next()
            new_cr.commit()
        except Exception:
            new_cr.rollback()  # error, rollback everything atomically
            raise
        finally:
            new_cr.close()
        return result
