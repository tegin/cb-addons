odoo.define("web_icon_widget.widget", function(require) {
    "use strict";

    var basic_fields = require("web.basic_fields");
    var field_registry = require("web.field_registry");
    var FieldIcon = basic_fields.FieldChar.extend({
        template: "FieldIcon",
        supportedFieldTypes: ["char"],
        _renderReadonly: function() {
            // Do Nothing
        },
        _renderEdit: function() {
            this.$input = this.$el.find("input");
        },
    });
    field_registry.add("icon", FieldIcon);
});
