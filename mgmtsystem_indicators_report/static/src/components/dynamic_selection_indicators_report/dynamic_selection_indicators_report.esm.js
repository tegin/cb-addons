/** @odoo-module **/

import {SelectionField} from "@web/views/fields/selection/selection_field";
import {registry} from "@web/core/registry";

export class DynamicSelectionIndicatorsReportField extends SelectionField {
    get options() {
        return this.props.record.data.selection_options.split(",").map((value) => {
            return [value, value];
        });
    }

    get string() {
        console.log(this.props.value, this.options);
        return this.props.value;
    }

    onChange(ev) {
        const value = JSON.parse(ev.target.value);

        this.props.update(value);
    }
}

DynamicSelectionIndicatorsReportField.supportedTypes = ["char"];
DynamicSelectionIndicatorsReportField.legacySpecialData = undefined;

registry
    .category("fields")
    .add("dynamic_selection_indicators_report", DynamicSelectionIndicatorsReportField);
