# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from dateutil import tz
from pytz import utc
from datetime import timedelta


def intervals_overlap(x1, x2, y1, y2):
    return x1 < y2 and y1 < x2


class MedicalSurgicalAppointmentRule(models.Model):

    _name = 'medical.surgical.appointment.rule'
    _description = 'Medical Surgical Appointment Rule'
    _inherit = ['mail.thread']

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
    surgeon_ids = fields.Many2many(
        'res.partner',
        domain=[
            ('allow_surgical_appointment', '=', True),
            ('is_practitioner', '=', True)
        ],
        string='Surgeons',
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
    validity_start = fields.Date()
    validity_stop = fields.Date()

    @api.model
    def check_rules(self, date_start, date_end, location,
                    surgeon=False, aux_surgeon=False):
        tz_name = self.env.user.tz
        rules = self

        date_start = fields.Datetime.from_string(date_start)
        date_end = fields.Datetime.from_string(date_end)

        if not self.env.context.get('no_tz', False):
            date_start = date_start.replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name))
            date_end = date_end.replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name))

        time_t = date_start.time()
        time_start = time_t.hour + time_t.minute/60
        time_t = date_end.time()
        time_end = time_t.hour + time_t.minute/60

        check_rules = self.search(
            [('location_id', '=', location.id)]).filtered(
            lambda r: r.is_valid(date_start, date_end))
        if surgeon:
            check_rules = check_rules.filtered(
                lambda r: (
                    r.rule_type != 'surgeon' or (
                        surgeon not in r.surgeon_ids and (
                            aux_surgeon not in r.surgeon_ids))
                ))
            aux_surgeon_id = aux_surgeon.id if aux_surgeon else -1
            check_rules |= self.search([
                '|', ('surgeon_ids', '=', aux_surgeon_id),
                ('surgeon_ids', '=', surgeon.id),
                ('location_id', '!=', location.id),
            ]).filtered(lambda r: r.is_valid(date_start, date_end))
        for rule in check_rules:
            if rule.rule_type in ['day', 'surgeon']:
                if int(rule.week_day) == date_start.weekday():
                    hour_from = 0.0 if rule.all_day else rule.hour_from
                    hour_to = 24.0 if rule.all_day else rule.hour_to
                    if intervals_overlap(
                        hour_from, hour_to, time_start, time_end
                    ):
                        rules |= rule
            else:
                start = fields.Datetime.from_string(rule.specific_from)
                end = fields.Datetime.from_string(rule.specific_to)
                if not self.env.context.get('no_tz', False):
                    start = start.replace(
                        tzinfo=tz.tzutc(),
                    ).astimezone(tz.gettz(tz_name))
                    end = end.replace(
                        tzinfo=tz.tzutc(),
                    ).astimezone(tz.gettz(tz_name))
                if intervals_overlap(
                    start, end, date_start, date_end
                ):
                    rules |= rule
        return rules

    @api.model
    def get_rules_date_location(self, date_start, date_stop, location):
        if isinstance(location, int):
            location = self.env['res.partner'].browse(location)
            location.exists()
        rules = self.with_context(no_tz=True).check_rules(
            date_start, date_stop, location
        )
        return [
            rule._get_rule_vals(date_start, date_stop) for rule in rules
        ]

    def _get_rule_vals(self, date_start, date_stop):
        start = fields.Datetime.from_string(date_start)
        stop = fields.Datetime.from_string(date_stop)
        if self.rule_type == 'specific':
            rule_start = fields.Datetime.from_string(self.specific_from)
            rule_stop = fields.Datetime.from_string(self.specific_to)
        else:
            # TODO: Improve the calculation, it might give problems on
            # change date days. Not critical
            start_tz = fields.Datetime.context_timestamp(self, start)
            today_tz = start_tz.replace(hour=0, minute=0, second=0)
            rule_start = (
                today_tz + timedelta(hours=self.hour_from)
            ).astimezone(utc).replace(tzinfo=None)
            rule_stop = (
                today_tz + timedelta(hours=self.hour_to)
            ).astimezone(utc).replace(tzinfo=None)
        start = max(start, rule_start)
        stop = min(stop, rule_stop)
        return {
            'type': 'rule',
            'id': - self.id,
            'name': self.display_name,
            'is_blocking': self.is_blocking,
            'date_start': fields.Datetime.to_string(start),
            'date_stop': fields.Datetime.to_string(stop),
        }

    @api.onchange('rule_type')
    def _onchange_rule_type(self):
        for record in self:
            if record.rule_type not in ['surgeon', 'day']:
                record.week_day = False
                record.all_day = False
                record.hour_from = False
                record.hour_to = False
            if record.rule_type != 'surgeon':
                record.surgeon_ids = [(6, 0, [])]
            record.is_blocking = record.rule_type != 'surgeon'

    def is_valid(self, date_start, date_end):
        for rule in self:
            validity_start = fields.Datetime.from_string(rule.validity_start)
            validity_stop = fields.Datetime.from_string(rule.validity_stop)
            if validity_start and validity_stop:
                return intervals_overlap(
                    date_start, date_end, validity_start, validity_stop
                )
            elif validity_start:
                return date_start >= validity_start
            elif validity_stop:
                return date_end <= validity_stop
            else:
                return True
