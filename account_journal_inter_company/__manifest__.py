# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Intercompany journal",
    "version": "14.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "summary": "Creates inter company relations",
    "sequence": 30,
    "category": "Accounting",
    "depends": ["account"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_inter_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
