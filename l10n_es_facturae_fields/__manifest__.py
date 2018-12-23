# © 2009 Alejandro Sanchez <alejandro@asr-oss.com>
# © 2015 Ismael Calvo <ismael.calvo@factorlibre.com>
# © 2015 Tecon
# © 2015 Omar Castiñeira (Comunitea)
# © 2016 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Campos extra de Factura-e",
    "version": "11.0.1.0.0",
    "author": "Creu Blanca, "
              "Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/l10n-spain",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_facturae",
        "base_sparse_field",
    ],
    "data": [
        "views/report_facturae.xml",
    ],
    "installable": True,
}
