# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Helpdesk",
    "summary": """
        Helpdesk from OCA with some modifications""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-addons",
    "depends": ["helpdesk_mgmt", "queue_job"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": [
        "security/ir.model.access.csv",
        "views/helpdesk_ticket_import_config.xml",
        "views/helpdesk_ticket_import.xml",
        "views/helpdesk_ticket.xml",
    ],
}
