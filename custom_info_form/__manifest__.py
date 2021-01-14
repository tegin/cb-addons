# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Custom Info Form",
    "summary": """
        Create and manage Forms using custom_info""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["base_custom_info"],
    "data": [
        "security/security.xml",
        "views/menu.xml",
        "views/custom_info_property.xml",
        "security/ir.model.access.csv",
        "views/custom_info_form.xml",
    ],
}
