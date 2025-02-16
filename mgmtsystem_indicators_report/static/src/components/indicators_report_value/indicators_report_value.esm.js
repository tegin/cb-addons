/** @odoo-module **/

const {Component} = owl;

import {Field} from "@web/views/fields/field";
import {registry} from "@web/core/registry";

export class IndicatorsReportValueField extends Component {
    get field_props() {
        var result = {
            name: "value_" + this.props.record.data.value_type,
            type: this.props.record.fields["value_" + this.props.record.data.value_type]
                .type,
            record: this.props.record,
        };
        if (this.props.record.data.value_type === "selection") {
            result.fieldInfo = {
                widget: "dynamic_selection_indicators_report",
                FieldComponent: registry
                    .category("fields")
                    .get("dynamic_selection_indicators_report"),
            };
        }
        return result;
    }
}

IndicatorsReportValueField.components = {Field};
IndicatorsReportValueField.template =
    "mgmtsystem_indicators_report.IndicatorsReportValueField";

console.log("HI!!!");
registry
    .category("fields")
    .add("mgmtsystem_indicators_report_value", IndicatorsReportValueField);
