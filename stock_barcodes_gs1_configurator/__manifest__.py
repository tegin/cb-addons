# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Barcodes Gs1 Configurator",
    "summary": """
        Simplify configuration of GS1 barcodes""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["stock_barcodes_gs1", "barcode_action"],
    "data": ["views/product.xml", "wizards/product_packaging_check.xml"],
}
