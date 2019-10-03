odoo.define('medical_surgical_appointment.AppointmentRenderer', function (require) {
"use strict";

var CalendarRenderer = require('web.CalendarRenderer');
var session = require('web.session');
var core = require('web.core');
var qweb = core.qweb;

var AppointmentRenderer= CalendarRenderer.extend({
    _initCalendar: function () {
        if (this.state.fc_options) {
            this.state.fc_options.slotEventOverlap = false;
        }
        return this._super.apply(this, arguments);
    },
    _renderEvents: function () {
        this.$calendar.fullCalendar('removeEvents');
        this.$calendar.fullCalendar(
            'addEventSource', this.state.data);
        this.$calendar.fullCalendar(
            'addEventSource', this.state.rules);
    },
    _eventRender: function (event) {
        if (event.record && event.record.type && event.record.type === 'rule') {
            var qweb_context = {
                event: event,
                record: event.record,
                widget: this,
                read_only_mode: this.read_only_mode,
                user_context: session.user_context,
                format: this._format.bind(this),
                fields: this.state.fields
            };
            if (_.isEmpty(qweb_context.record)) {
                return '';
            }
            return qweb.render("calendar-rule-box", qweb_context);
        }
        return this._super.apply(this, arguments);
    },
});

return AppointmentRenderer;

});