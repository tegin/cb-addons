# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE pos_session
        SET rescue = TRUE,
            state = 'closing_control'
        WHERE state = 'pending_approval'
        """,
    )
