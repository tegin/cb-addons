odoo.define('medical_surgical_appointment.AppointmentModel', function (require) {
    "use strict";

    var CalendarModel = require('web.CalendarModel');
    var core = require('web.core');
    var fieldUtils = require('web.field_utils');
    var session = require('web.session');

    function dateToServer (date) {
        return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
    }
    function sec2time(timeInSeconds) {
        var pad = function(num, size) { return ('00' + num).slice(size * -1); },
        time = parseFloat(timeInSeconds).toFixed(3),
        hours = Math.floor(time),
        minutes = Math.floor((time - hours) * 60),
        seconds = Math.floor(((time - hours)* 60 - minutes)*60),
        milliseconds = time.slice(-3);

        return pad(hours, 2) + ':' + pad(minutes, 2) + ':' + pad(seconds, 2);
    }

    var AppointmentModel= CalendarModel.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.location_start_date = 8;
            this.location_end_date = 22;
        },
        _getFullCalendarOptions: function () {
             var result = this._super.apply(this, arguments);
             result.allDaySlot = false;
             result.minTime = sec2time(this.location_start_date);
		     result.maxTime = sec2time(this.location_end_date);
             return result
        },
        setLocation: function (location_id, location_name) {
            this.location_id = location_id;
            this.location_name = location_name;
            this.location_start_date = 8;
            this.location_end_date = 22;
        },
        load: function (params) {
            var result = this._super.apply(this, arguments);
            this._getLocations();
            return result;
        },
        _getLocations: function () {
            var self = this;
            this._rpc({model: this.modelName, method: 'get_locations', args: []}).then(
                function(locations){
                    self.locations = locations;
                    self.location_id =locations[0][0];
                    self.location_name = locations[0][1];
                }
            );
        },
        _getRangeDomain: function () {
            var domain = this._super.apply(this, arguments);
            domain.push(['location_id', '=', this.location_id]);
            return domain;
        },
        _loadCalendar: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._rpc({
                    model: 'medical.surgical.appointment.rule',
                    method: 'get_rules_date_location',
                    args: [dateToServer(self.data.start_date), dateToServer(self.data.end_date), self.location_id],
                    context: self.data.context,
                    fields: self.fieldNames,
                    domain: self.data.domain.concat(self._getRangeDomain()).concat(self._getFilterDomain())
                })
                .then(function (events) {
                    self.data.rules = _.map(events, self._recordToCalendarRules.bind(self));
                });
            });
        },
        _recordToCalendarRules: function (rule) {
            var date_start = fieldUtils.parse['datetime'](
                rule.date_start, false, {isUTC: true});
            var date_stop = fieldUtils.parse['datetime'](
                rule.date_stop, false, {isUTC: true});
            date_start.add(this.getSession().getTZOffset(date_start), 'minutes');
            date_stop.add(this.getSession().getTZOffset(date_stop), 'minutes');
            return {
                'record': rule,
                'start': date_start,
                'end': date_stop,
                'r_start': date_start,
                'r_end': date_stop,
                'title': rule.name,
                'allDay': false,
                'id': rule.id,
                'color': rule.is_blocking? 'red' : 'yellow',
                'textColor': rule.is_blocking? 'white' : 'black',
                'attendees': [],
            };
        }
    });

    return AppointmentModel;

});