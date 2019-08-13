from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class HolidaysCountReport(models.AbstractModel):
    _name = "report.cb_number_of_holidays_report.report_holidays_count"

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get("form"):
            raise UserError(
                _("Form content is missing, this report cannot be printed.")
            )

        date_from = data["form"]["date_from"]
        date_to = data["form"]["date_to"]

        docs = []

        for employee in self.env["hr.employee"].browse(
            data["form"]["employee_ids"]
        ):
            holidays = self.env["hr.holidays"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("type", "=", "remove"),
                    ("date_from", "<=", date_to),
                    ("date_to", ">=", date_from),
                    ("state", "=", "validate"),
                    ("count_in_hours", "=", False),
                ]
            )

            days_count = 0.0
            date_from_day = fields.Datetime.from_string(date_from)
            date_to_day = fields.Datetime.from_string(date_to)
            date_to_day += timedelta(days=1)
            for holiday in holidays:
                if date_from >= holiday.date_from and (
                    date_to <= holiday.date_to
                ):
                    days = (date_to_day - date_from_day).days
                elif date_from < holiday.date_from and (
                    date_to > holiday.date_to
                ):
                    days = abs(holiday.number_of_days)
                elif date_from >= holiday.date_from and (
                    date_to >= holiday.date_to
                ):
                    days = self.env["hr.holidays"]._get_number_of_days(
                        date_from, holiday.date_to, False
                    )
                else:
                    days = self.env["hr.holidays"]._get_number_of_days(
                        holiday.date_from,
                        fields.Datetime.to_string(date_to_day),
                        False,
                    )
                days_count += days
            docs.append({"employee": employee.name, "num_of_days": days_count})

        return {
            "doc_ids": data["ids"],
            "doc_model": data["model"],
            "date_from": date_from,
            "date_to": date_to,
            "docs": docs,
        }
