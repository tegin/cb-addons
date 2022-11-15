# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    (
        "account.bank.statement.import.n43.multi",
        "account.statement.import.n43.multi",
    ),
]

_table_renames = [
    (
        "account_bank_statement_import.n43.multi",
        "account_statement_import.n43.multi",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
