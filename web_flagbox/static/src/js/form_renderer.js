odoo.define("web_flag_box.form_renderer", function(require) {
    "use strict";

    var FormRenderer = require("web.FormRenderer");
    var config = require("web.config");
    var core = require("web.core");
    var py = window.py;
    var _t = core._t;

    var DECORATIONS = [
        "decoration-danger",
        "decoration-info",
        "decoration-muted",
        "decoration-primary",
        "decoration-success",
        "decoration-warning",
        "decoration-light",
    ];

    FormRenderer.include({
        _renderTagEmptyflag: function(node) {
            var $tag = $("<i>").addClass("flag oe_stat_button flag emptyflag");
            $tag.append(_.map(node.children, this._renderNode.bind(this)));
            return $tag;
        },
        _renderTagFlag: function(node) {
            var self = this;
            var rowDecorations = _.chain(node.attrs)
                .pick(function(value, key) {
                    return DECORATIONS.indexOf(key) >= 0;
                })
                .mapObject(function(value) {
                    return py.parse(py.tokenize(value));
                })
                .value();
            var $tag = $("<i>").addClass("flag oe_stat_button");
            if (node.attrs.icon) {
                $("<div>")
                    .addClass("fa fa-fw o_button_icon")
                    .addClass(node.attrs.icon)
                    .appendTo($tag);
            }
            if (node.attrs.string) {
                $("<span>")
                    .text(node.attrs.string)
                    .appendTo($tag);
            }
            $tag.append(_.map(node.children, this._renderNode.bind(this)));
            this._handleAttributes($tag, node);
            this._registerModifiers(node, this.state, $tag);
            _.each(rowDecorations, function(expr, decoration) {
                var cssClass = decoration.replace("decoration", "flag");
                $tag.toggleClass(
                    cssClass,
                    py.PY_isTrue(py.evaluate(expr, self.state.data))
                );
            });

            if (config.debug || node.attrs.help) {
                this._addButtonTooltip(node, $tag);
            }
            return $tag;
        },
        _renderTagFlagbox: function(node) {
            var self = this;
            var $result = $("<div>", {class: "oe_flag_box"});
            var buttons = _.map(node.children, function(child) {
                if (child.tag === "button") {
                    return self._renderStatButton(child);
                }
                return self._renderNode(child);
            });
            var buttons_partition = _.partition(buttons, function($button) {
                return $button.is(".o_invisible_modifier");
            });
            var invisible_buttons = buttons_partition[0];
            var visible_buttons = buttons_partition[1];

            // Get the unfolded buttons according to window size
            var nb_buttons = [7, 13, 19, 21, 23, 25, 27][config.device.size_class];
            var unfolded_buttons = visible_buttons
                .slice(0, nb_buttons)
                .concat(invisible_buttons);

            // Get the folded buttons
            var folded_buttons = visible_buttons.slice(nb_buttons);
            if (folded_buttons.length === 1) {
                unfolded_buttons = buttons;
                folded_buttons = [];
            }

            // Toggle class to tell if the button box is full
            // (LESS requirement)
            var full = visible_buttons.length > nb_buttons;
            $result.toggleClass("o_full", full).toggleClass("o_not_full", !full);

            // Add the unfolded buttons
            _.each(unfolded_buttons, function($button) {
                $button.appendTo($result);
            });
            // Add the dropdown with folded buttons if any
            if (folded_buttons.length) {
                $result.append(
                    $("<button>", {
                        type: "button",
                        class:
                            "btn btn-sm oe_stat_button" +
                            "o_button_more dropdown-toggle",
                        "data-toggle": "dropdown",
                        text: _t("More"),
                    })
                );
                var $ul = $("<ul>", {
                    class: "dropdown-menu o_dropdown_more",
                    role: "menu",
                });
                _.each(folded_buttons, function($button) {
                    $("<li>")
                        .appendTo($ul)
                        .append($button);
                });
                $ul.appendTo($result);
            }

            this._handleAttributes($result, node);
            this._registerModifiers(node, this.state, $result);
            return $result;
        },
    });
});
