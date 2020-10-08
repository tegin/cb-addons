from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """ Trying to fill the source expense sheet in payments """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env["credit.control.communication"].search([]).write({"state": "sent"})
        for record in env["credit.control.line"].search([]):
            record.write({"original_balance_due": record.balance_due})
