# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Product nomenclature",
    "version": "12.0.1.0.0",
    "author": "Creu Blanca",
    "category": "Product",
    "depends": ["product", "sales_team"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_nomenclature_product_views.xml",
        "views/product_nomenclature_views.xml",
    ],
    "website": "https://github.com/Eficent/cb-addons",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
