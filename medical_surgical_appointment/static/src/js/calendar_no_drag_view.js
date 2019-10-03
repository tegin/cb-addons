odoo.define('medical_surgical_appointment.CalendarView', function (require) {
"use strict";

var CalendarView = require('web.CalendarView');

var CalendarViewNoCreate = CalendarView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        var arch = viewInfo.arch;
        var attrs = arch.attrs;
        if (params.context['no_drag']){
            this.loadParams.creatable = true;
        }
    },
});

});