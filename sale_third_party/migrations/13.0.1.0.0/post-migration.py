# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    sale_orders = env["sale.order"].search([("third_party_order", "=", True)])
    # We will execute the change only for the possible candidates, all the others, data
    # should be right
    sale_orders._compute_third_party_residual()
