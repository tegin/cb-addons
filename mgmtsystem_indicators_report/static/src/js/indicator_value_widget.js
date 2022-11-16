odoo.define("mgmtsystem_indicators_report.ValueWidget", function (require) {
    "use strict";
    /*
       This code modifies the "group" tag allowing to add
       a group of fields as a single field in a table column.
    */
    var ListRenderer = require("web.ListRenderer");
    var relational_fields = require("web.relational_fields");
    ListRenderer.include({
        init: function (parent, state, params) {
            if (parent !== undefined && parent.record !== undefined) {
                var new_context = parent.record.getContext({
                    additionalContext: parent.attrs.context || {},
                });
                if (new_context.hide_delete_create) {
                    params.addCreateLine = false;
                    params.addTrashIcon = false;
                }
            }
            this._super.apply(this, arguments);
        },
        _renderBodyCell: function (record, node, colIndex, options) {
            if (
                node.tag === "field" &&
                node.attrs &&
                node.attrs.widget === "mgmtsystem_indicator_report" &&
                record.data.value_type
            ) {
                var final_child = undefined;
                _.each(node.children, function (child) {
                    if (child.attrs.name === "value_" + record.data.value_type) {
                        final_child = child;
                    }
                });
                console.log(final_child);
                if (final_child !== undefined) {
                    if (typeof final_child.attrs.modifiers !== "object") {
                        final_child.attrs.modifiers = final_child.attrs.modifiers
                            ? JSON.parse(final_child.attrs.modifiers)
                            : {};
                    }
                    console.log(final_child, record, colIndex, options);
                    return this._renderBodyCell(record, final_child, colIndex, options);
                }
            }
            return this._super.apply(this, arguments);
        },
    });

    relational_fields.FieldX2Many.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            if (
                this.attrs.options.hide_delete_create &&
                record.data[this.attrs.options.hide_delete_create]
            ) {
                this.activeActions.create = false;
                this.activeActions.delete = false;
                this.activeActions.addTrashIcon = false;
            }
        },
    });
});
