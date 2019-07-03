odoo.define('medical_surgical_appointment.CalendarView', function (require) {
"use strict";

var CalendarView = require('web.CalendarView');
var session = require("web.session");

var CalendarViewNoCreate = CalendarView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        var arch = viewInfo.arch;
        var attrs = arch.attrs;
        console.log('hola')
        console.log(session.user_context)
        if (session.user_context['no_create_calendar']){
            this.loadParams.creatable = false;
        }
    },
});

return CalendarViewNoCreate;

});