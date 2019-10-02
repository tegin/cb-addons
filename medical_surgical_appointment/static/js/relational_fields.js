odoo.define('medical_surgical_appointment.relational_fields', function (require) {
"use strict";

    var RelationalFields = require('web.relational_fields');

    var FieldMany2One = RelationalFields.FieldMany2One.include({
        _search: function (search_val) {
            var res = this._super.apply(this, arguments);
            console.log(res);
            if (false) {
                var context = this.record.getContext(this.recordParams);
                var domain = this.record.getDomain(this.recordParams);
                this._rpc({
                    model: this.field.relation,
                    method: 'name_search',
                    kwargs: {
                        name: search_val,
                        args: domain,
                        operator: "ilike",
                        limit: 160,
                        context: context,
                    },
                })
                .then(this._searchCreatePopup.bind(this, "search"));
            }
            return res
        }
    });
});