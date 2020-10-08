# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Convert custom_text fields to Html on policy_level
    """
    cr = env.cr
    openupgrade.copy_columns(
        cr,
        {
            "credit_control_line": [
                ("balance_due", "original_balance_due", None),
            ]
        },
    )
