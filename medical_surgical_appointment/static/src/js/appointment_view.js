odoo.define('medical_surgical_appointment.AppointmentView', function (require) {
"use strict";

var CalendarView = require('web.CalendarView');
var AppointmentController = require('medical_surgical_appointment.AppointmentController');
var AppointmentModel = require('medical_surgical_appointment.AppointmentModel');
var AppointmentRenderer = require('medical_surgical_appointment.AppointmentRenderer');
var view_registry = require('web.view_registry');

var AppointmentView = CalendarView.extend({
    config: {
        Model: AppointmentModel,
        Controller: AppointmentController,
        Renderer: AppointmentRenderer,
    },
    searchable: false,
});

view_registry
    .add('appointment', AppointmentView);

return AppointmentView;

});