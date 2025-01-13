/** @odoo-module **/
import {Component, xml} from "@odoo/owl";
import {registry} from "@web/core/registry";

class HistoryBack extends Component {
    setup() {
        this.env.config.historyBack();
    }
}
// We need to add a template to the component so that it can be rendered, but it will not be used...
HistoryBack.template = xml`<div></div>`;

registry.category("actions").add("history_back", HistoryBack);
