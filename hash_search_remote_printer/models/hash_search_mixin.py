# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class HashSearchMixin(models.AbstractModel):
    _inherit = 'hash.search.mixin'

    def _get_printer(self):
        behaviour = self.remote.with_context(
            printer_usage='label'
        ).get_printer_behaviour()
        if 'printer' not in behaviour:
            return super()._get_printer()
        printer = behaviour.pop('printer')
        return printer
