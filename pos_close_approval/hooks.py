from odoo import _
from odoo.exceptions import UserError

from odoo.addons.point_of_sale.models.pos_config import PosConfig


def post_load_hook():  # noqa: C901
    if not hasattr(PosConfig, "write_close_approval_original"):
        old_function = PosConfig.write
        PosConfig.write_close_approval_original = old_function

    def new_write(self, vals):
        opened_session = self.mapped("session_ids").filtered(
            lambda s: s.state not in ["closed", "pending_approval"]
        )
        if opened_session:
            raise UserError(
                _(
                    "Unable to modify this PoS Configuration because there "
                    "is an open PoS Session based on it."
                )
            )
        result = super(PosConfig, self).write(vals)

        self.sudo()._set_fiscal_position()
        self.sudo()._check_modules_to_install()
        self.sudo()._check_groups_implied()
        return result

    PosConfig.write = new_write
