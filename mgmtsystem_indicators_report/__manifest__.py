# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mgmtsystem Indicators Report",
    "summary": """
        This module allows to
        manage quality indicators data""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/cb-addons",
    "depends": [
        "account",
        "mgmtsystem_nonconformity",
        "mail",
        "uom",
        "web_editor",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "templates/assets.xml",
        "wizards/indicators_report_from_template.xml",
        "report/indicators_report_views.xml",
        "views/uom_uom.xml",
        "views/mgmtsystem_indicators_report.xml",
        "views/mgmtsystem_indicators_report_template.xml",
        "views/mgmtsystem_indicator_concept.xml",
    ],
    "demo": [],
}
