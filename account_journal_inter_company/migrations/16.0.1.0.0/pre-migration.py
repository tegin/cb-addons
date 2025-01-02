# Copyright 2025 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Migrate Analytic Accounts to Analytic Distributions on Assets and Profiles"""
    openupgrade.add_fields(
        env,
        [
            (
                "account_id",
                "res.inter.company",
                "res_inter_company",
                "many2one",
                False,
                "account_journal_inter_company",
                None,
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE res_inter_company ric
            SET account_id = journal.default_account_id
            FROM account_journal journal
            WHERE journal.id = ric.journal_id
        """,
    )
