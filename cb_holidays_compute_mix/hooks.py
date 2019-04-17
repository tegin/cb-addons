from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.ref('hr_holidays.action_open_ask_holidays_calendar'):
            env.ref('hr_holidays.action_open_ask_holidays_calendar').unlink()
