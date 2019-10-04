# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from datetime import datetime, time
from dateutil import tz


def intervals_overlap(x1, x2, y1, y2):
    return x1 < y2 and y1 < x2


class MedicalSurgicalAppointmentRule(models.Model):

    _name = 'medical.surgical.appointment.rule'
    _description = 'Medical Surgical Appointment Rule'

    name = fields.Char()
    active = fields.Boolean(default=True)
    location_id = fields.Many2one(
        string="Location",
        comodel_name='res.partner',
        domain=[
            ('is_location', '=', True),
            ('allow_surgical_appointment', '=', True)
        ],
        track_visibility=True,
        ondelete='restrict',
        required=True,
    )
    surgeon_id = fields.Many2one(
        'res.partner',
        domain=[
            ('allow_surgical_appointment', '=', True),
            ('is_practitioner', '=', True)
        ],
        string='Surgeon',
    )

    is_blocking = fields.Boolean()

    rule_type = fields.Selection([
        ('day', 'By day'),
        ('surgeon', 'By surgeon'),
        ('specific', 'Close Specific Day'),
    ])

    # By day
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ])
    all_day = fields.Boolean()
    hour_from = fields.Float()
    hour_to = fields.Float()

    # Specific
    specific_from = fields.Datetime()
    specific_to = fields.Datetime()

    # Validity dates
    valid = fields.Boolean(compute='_compute_valid', store=True)
    validity_start = fields.Datetime()
    validity_stop = fields.Datetime()

    @api.model
    def check_rules(self, date_start, date_end, location_id):
        rules = self
        date_start = fields.Datetime.from_string(date_start)
        date_end = fields.Datetime.from_string(date_end)
        utz = self.env.user.tz
        time_t = date_start.time().replace(tzinfo=tz.gettz(utz))
        time_start = time_t.hour + time_t.minute/60
        time_t = date_end.time().replace(tzinfo=tz.gettz(utz))
        time_end = time_t.hour + time_t.minute/60

        domain = [('valid', '=', True), ('location_id', '=', location_id)]
        for record in self.search(domain):
            if record.rule_type in ['day', 'surgeon']:
                import logging
                if int(record.week_day) == date_start.weekday():
                    hour_from = 0.0 if record.all_day else record.hour_from
                    hour_to = 24.0 if record.all_day else record.hour_to
                    logging.info([hour_from, hour_to, time_start, time_end])
                    if intervals_overlap(
                            hour_from, hour_to, time_start, time_end
                    ):
                        rules |= record
            else:
                start = fields.Datetime.from_string(record.specific_from)
                end = fields.Datetime.from_string(record.specific_to)
                if intervals_overlap(
                        start, end, date_start, date_end
                ):
                    rules |= record
        return rules

    @api.model
    def get_rules_date_location(self, date, location_id):
        utz = self.env.user.tz
        date_t = fields.Date.from_string(date)
        date_start = fields.Datetime.to_string(
            datetime.combine(date_t, time(
                0, 0, 0, 0, tzinfo=tz.gettz(utz))),
        )
        date_end = fields.Datetime.to_string(
            datetime.combine(
                date_t, time(23, 59, 59, 99999, tzinfo=tz.gettz(utz))
            )
        )
        rules = self.check_rules(date_start, date_end, location_id)
        return [rule.read() for rule in rules]

    @api.onchange('rule_type')
    def _onchange_rule_type(self):
        for record in self:
            if record.rule_type != 'by_day':
                record.week_day = False
                record.all_day = False
                record.hour_from = False
                record.hour_to = False
            record.is_blocking = record.rule_type != 'surgeon'

    @api.depends('validity_start', 'validity_stop')
    def _compute_valid(self):
        now = fields.Datetime.from_string(fields.Datetime.now())
        for rule in self:
            validity_start = fields.Datetime.from_string(rule.validity_start)
            validity_stop = fields.Datetime.from_string(rule.validity_stop)
            if validity_start and validity_stop:
                rule.valid = (now <= validity_stop) and (now >= validity_start)
            elif validity_start:
                rule.valid = now >= validity_start
            elif validity_stop:
                rule.valid = now <= validity_stop
            else:
                rule.valid = True
