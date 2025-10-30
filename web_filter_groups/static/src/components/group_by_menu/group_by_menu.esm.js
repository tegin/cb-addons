/** @odoo-module **/

import {GroupByMenu} from "@web/search/group_by_menu/group_by_menu";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {onWillStart} from "@odoo/owl";

patch(GroupByMenu.prototype, "web_filter_groups.GroupByMenu", {
    setup() {
        this._super.apply(this, arguments);
        this.user = useService("user");
        onWillStart(async () => {
            this.showFilter = await this.user.hasGroup(
                "web_filter_groups.filter_group"
            );
        });
    },
    get hideCustomGroupBy() {
        return !this.showFilter || this._super.apply(this, arguments);
    },
});
