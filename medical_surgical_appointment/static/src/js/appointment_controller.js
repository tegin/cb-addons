odoo.define('medical_surgical_appointment.AppointmentController', function (require) {
"use strict";

var CalendarController = require('web.CalendarController');
var core = require('web.core');
var QWeb = core.qweb;

var AppointmentController = CalendarController.extend({
    custom_events: _.extend({}, CalendarController.prototype.custom_events, {
        changeLocation: '_onChangeLocation',
        setLocations: '_onSetLocations',
    }),
    _onChangeLocation: function (event) {
        this.model.setLocation(event.data.location);
        this.reload();
    },
    _onChangeDate: function (event) {
        this.model.setDate(event.data.date);
        this.reload();
    },
    renderButtons: function ($node) {
        var self = this;
        this.$buttons = $(QWeb.render("AppointmentView.buttons", {'widget': this}));
        this.$buttons.on('click', 'button.o_calendar_button_new', function () {
            self.trigger_up('switch_view', {view_type: 'form'});
        });

        _.each(['prev', 'today', 'next'], function (action) {
            self.$buttons.on('click', '.o_calendar_button_' + action, function () {
                self.model[action]();
                self.reload();
            });
        });

        this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');
        this.$locations = $(QWeb.render("AppointmentView.Locations", {
            'widget': this,
        }));
        this.$locations.on('click', '.dropdown_name', function () {
            self.$locations.toggleClass('o_open_menu')
        })
        self.$locations.find('.appointment_select_' + this.model.location_id).toggleClass("selected")
        _.each(this.model.locations, function (location_vals) {
            self.$locations.on('click', '.appointment_select_' + location_vals[0], function () {
                self.$locations.find('.appointment_select_' + self.model.location_id).toggleClass("selected")
                self.model.setLocation(location_vals[0], location_vals[1]);
                self.$locations.find('.appointment_select_' + location_vals[0]).toggleClass("selected");
                self.$locations.find('.dropdown_name').text(location_vals[1]);
                self.reload();
            })
        });
        this.$buttons.find('.o_calendar_locations').replaceWith(this.$locations);
        if ($node) {
            this.$buttons.appendTo($node);
        } else {
            this.$('.o_calendar_buttons').replaceWith(this.$buttons);
        }
        this.reload();
    },
    _onOpenCreate: function (event) {
        this.context['default_location_id'] = this.model.location_id;
        return this._super.apply(this, arguments);
    },
    _onOpenEvent: function (event) {
        if (event.data.record.type && event.data.record.type === 'rule')
            return;
        return this._super.apply(this, arguments);
    },
});

return AppointmentController ;

});