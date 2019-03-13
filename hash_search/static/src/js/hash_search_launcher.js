odoo.define('hash_search.hash_search_launcher', function (require) {
    "use strict";

    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget'); /**
     * Menu item appended in the systray part of the navbar
     *
     * The menu item adds the possibility to scan QR tags.
     **/
    var LauncherMenu = Widget.extend({
        template:'hash_search_launcher.view.Menu',
        events: {
            "click": "on_click_find_document",
        },

        on_click_find_document: function(){
            var context = {};
            context.default_model = 'hash.search';
            context.default_method ='find_hash';
            return this.do_action({
                type: 'ir.actions.act_window',
                name: 'Search QR',
                res_model:  'barcode.action',
                views: [[false, 'form']],
                target: 'new',
                context:context,
            });
        },
    });


    SystrayMenu.Items.push(LauncherMenu);
    return {
        LauncherMenu: LauncherMenu,
    };
});
