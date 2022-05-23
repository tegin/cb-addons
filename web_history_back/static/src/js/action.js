odoo.define("web_history_back.history_back", function (require) {
    "use strict";
    var core = require("web.core");

    function HistoryBack(parent) {
        parent.trigger_up("history_back");
    }

    core.action_registry.add("history_back", HistoryBack);
});
