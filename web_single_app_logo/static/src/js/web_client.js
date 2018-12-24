odoo.define('web_single_app_logo.WebClient', function (require) {
    "use strict";
    var Client = require('web.WebClient');
    Client.include({
        // The function is rewritten in order to not
        // refresh the logo with the company
        update_logo: function () {
            return;
        },
    });
});
