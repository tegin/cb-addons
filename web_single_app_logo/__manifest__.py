# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Web Single App Logo",
    "version": "16.0.1.0.0",
    "website": "https://github.com/tegin/cb-addons",
    "author": "CreuBlanca",
    "license": "AGPL-3",
    "category": "Website",
    "summary": "Allows to define a single app logo",
    "depends": ["base_setup", "web"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/template_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_single_app_logo/static/src/js/web_client.js",
        ],
    },
}
