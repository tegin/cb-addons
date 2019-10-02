# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    def get_access_action(self, *args, **kwargs):
        if not self.env.context.get("no_website_action", False):
            return super().get_access_action(*args, **kwargs)
        return False
