# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlid_renames = [
    (
        "l10n_es_iva_soportado_no_deducible.account_tax_template_p_iva10_nd",
        "l10n_es.account_tax_template_p_iva10_nd",
    ),
    (
        "l10n_es_iva_soportado_no_deducible.account_tax_template_p_iva4_nd",
        "l10n_es.account_tax_template_p_iva4_nd",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
