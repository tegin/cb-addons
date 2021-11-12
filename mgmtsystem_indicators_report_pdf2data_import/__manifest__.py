# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mgmtsystem Indicators Report Pdf2data Import",
    "summary": """
        This addon allows to create a indicators report
        extracting the data from a pdf""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["mgmtsystem_indicators_report", "edi_pdf2data"],
    "data": [
        "views/pdf2data_template.xml",
        "views/mgmtsystem_menu.xml",
        "data/edi_pdf2data_type.xml",
    ],
    "demo": [],
}
