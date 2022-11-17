# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Web Register Login",
    "summary": """
        Register Logins""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-addons",
    "depends": ["base_remote"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_users_access_log_security.xml",
        "views/base_remote.xml",
        "views/res_users_access_log.xml",
        "views/res_users.xml",
    ],
}
