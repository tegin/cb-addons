# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Safe Box with PoS",
    "version": "13.0.1.0.0",
    "author": "Eficent, Creu Blanca",
    "depends": ["safe_box", "pos_close_approval", "pos_session_pay_invoice"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pos_session_validation_views.xml",
        "views/pos_session_views.xml",
        "views/pos_config_views.xml",
        "views/safe_box_group_views.xml",
        "views/safe_box_coin_views.xml",
    ],
    "website": "https://github.com/eficent/cb-addons",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
