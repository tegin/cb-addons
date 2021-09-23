# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade

_field_adds = [
    (
        "third_party_customer_in_residual",
        "sale.order",
        "sale_order",
        "monetary",
        False,
        "sale_third_party",
    ),
    (
        "third_party_customer_in_residual_company",
        "sale.order",
        "sale_order",
        "monetary",
        False,
        "sale_third_party",
    ),
    (
        "third_party_customer_out_residual",
        "sale.order",
        "sale_order",
        "monetary",
        False,
        "sale_third_party",
    ),
    (
        "third_party_customer_out_residual_company",
        "sale.order",
        "sale_order",
        "monetary",
        False,
        "sale_third_party",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _field_adds)
