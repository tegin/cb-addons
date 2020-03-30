# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def _get_document_quick_access_label_printer(self):
        behaviour = self.remote.with_context(
            printer_usage="label"
        ).get_printer_behaviour()
        if "printer" not in behaviour:
            return False
        printer = behaviour.pop("printer")
        return printer
