odoo.define('cb_departments_chart.OrgChart', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var concurrency = require('web.concurrency');
var core = require('web.core');
var field_registry = require('web.field_registry');

var QWeb = core.qweb;
var _t = core._t;

var FieldDepartmentChart = AbstractField.extend({

    events: {
        "click .o_department_redirect": "_ondepartmentRedirect",
        "click .o_department_sub_redirect": "_ondepartmentSubRedirect",
    },
    /**
     * @constructor
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.dm = new concurrency.DropMisordered();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Get the chart data through a rpc call.
     *
     * @private
     * @param {integer} department_id
     * @returns {Deferred}
     */
    _getOrgData: function (department_id) {
        var self = this;
        return this.dm.add(this._rpc({
            route: '/cb_departments_chart/get_org_chart',
            params: {
                department_id: department_id,
            },
        })).then(function (data) {
            self.orgData = data;
        });
    },
    /**
     * @override
     * @private
     */
    _render: function () {
        if (!this.recordData.id) {
            return this.$el.html(QWeb.render("hr_department_chart", {
                departments: [],
                children: [],
            }));
        }

        var self = this;
        return this._getOrgData(this.recordData.id).then(function () {
            self.$el.html(QWeb.render("hr_department_chart", self.orgData));
            self.$('[data-toggle="popover"]').each(function () {
                $(this).popover({
                    html: true,
                    title: function () {
                        var $title = $(QWeb.render('hr_orgchart_emp_popover_title', {
                            department: {
                                name: $(this).data('emp-name'),
                                id: $(this).data('emp-id'),
                            },
                        }));
                        $title.on('click',
                            '.o_department_redirect', _.bind(self._ondepartmentRedirect, self));
                        return $title;
                    },
                    container: 'body',
                    placement: 'left',
                    trigger: 'focus',
                    content: function () {
                        var $content = $(QWeb.render('hr_orgchart_emp_popover_content', {
                            department: {
                                id: $(this).data('emp-id'),
                                name: $(this).data('emp-name'),
                                direct_sub_count: parseInt($(this).data('emp-dir-subs')),
                                indirect_sub_count: parseInt($(this).data('emp-ind-subs')),
                            },
                        }));
                        $content.on('click',
                            '.o_department_sub_redirect', _.bind(self._ondepartmentSubRedirect, self));
                        return $content;
                    },
                    template: QWeb.render('hr_orgchart_emp_popover', {}),
                });
            });
        });
    },

    _ondepartmentRedirect: function (event) {
        event.preventDefault();
        var department_id = parseInt($(event.currentTarget).data('department-id'));
        return this.do_action({
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current',
            res_model: 'hr.department',
            res_id: department_id,
        });
    },
    /**
     * Redirect to the sub department form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Deferred} action loaded
     */
    _ondepartmentSubRedirect: function (event) {
        event.preventDefault();
        var department_id = parseInt($(event.currentTarget).data('department-id'));
        var department_name = $(event.currentTarget).data('department-name');
        var type = $(event.currentTarget).data('type') || 'direct';
        var domain = [['parent_id', '=', department_id]];
        var name = _.str.sprintf(_t("Direct Subordinates of %s"), department_name);
        if (type === 'total') {
            domain = ['&', ['parent_id', 'child_of', department_id], ['id', '!=', department_id]];
            name = _.str.sprintf(_t("Subordinates of %s"), department_name);
        } else if (type === 'indirect') {
            domain = ['&', '&',
                ['parent_id', 'child_of', department_id],
                ['parent_id', '!=', department_id],
                ['id', '!=', department_id]
            ];
            name = _.str.sprintf(_t("Indirect Subordinates of %s"), department_name);
        }
        if (department_id) {
            return this.do_action({
                name: name,
                type: 'ir.actions.act_window',
                view_mode: 'kanban,list,form',
                views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
                target: 'current',
                res_model: 'hr.department',
                domain: domain,
                res_id: department_id,
            });
        }
    },
});

field_registry.add('hr_department_chart',  FieldDepartmentChart);

return FieldDepartmentChart;

});
