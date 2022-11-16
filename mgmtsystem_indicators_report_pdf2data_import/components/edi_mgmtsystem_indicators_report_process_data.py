# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.component.core import Component


class EDIBackendInputComponentMixin(Component):
    _inherit = "edi.component.process_data.mixin"
    _name = "edi.component.process_data.mgmtsystem.indicators.report"
    _usage = "process_data"
    _backend_type = "import_data"
    _exchange_type = None
    _process_type = "mgmtsystem.indicators.report"

    def _get_parsed_pdf2data_values(self, model, data_extracted):
        report_values = {}
        for field in data_extracted:
            if field in model._fields:
                report_values[field] = data_extracted[field]
        line_values = [
            (0, 0, self._get_parsed_pdf2data_indicator_ids(line))
            for line in data_extracted.get("lines")
        ]
        report_values.update({"indicator_ids": line_values})
        return report_values

    def _get_parsed_pdf2data_indicator_ids(self, line):
        return {"name": line.get("concept"), "value": line.get("value")}

    def _generate_from_template(self, data, template):
        report_template = template.mgmtsystem_indicator_template_id
        report = report_template._generate_report()
        vals = {}
        for field in data:
            if field in report._fields:
                vals[field] = data[field]
        line_vals = []
        for line in data.get("lines"):
            if line.get("concept"):
                template_indicator = report.indicator_ids.filtered(
                    lambda r: r.name == line.get("concept")
                )
                if template_indicator:
                    if template_indicator.value_type and line.get("value"):
                        line_vals.append(
                            (
                                1,
                                template_indicator.id,
                                {
                                    "value_%s"
                                    % template_indicator.value_type: line.get("value")
                                },
                            )
                        )
                    elif line.get("value"):
                        line_vals.append(
                            (
                                1,
                                template_indicator.id,
                                {"value": line.get("value")},
                            )
                        )
                else:
                    line_vals.append(
                        (0, 0, self._get_parsed_pdf2data_indicator_ids(line))
                    )
        vals.update({"indicator_ids": line_vals})
        report.write(vals)
        return report

    def process_data(self, data, template, file):
        if not template.mgmtsystem_indicator_template_id:
            model = self.env["mgmtsystem.indicators.report"]
            record = model.create(self._get_parsed_pdf2data_values(model, data))
        else:
            record = self._generate_from_template(data, template)
        record.update({"report_pdf": file})
        self.exchange_record.write({"model": record._name, "res_id": record.id})
