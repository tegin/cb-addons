# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Web Filter Groups",
    "summary": """Make Advanced filters hidden if you are not in a certain group""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,CreuBlanca",
    "website": "https://github.com/tegin/cb-addons",
    "depends": ["web"],
    "data": ["security/security.xml"],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "web_filter_groups/static/src/**/*.esm.js",
            "web_filter_groups/static/src/**/*.xml",
        ]
    },
}
