/** @odoo-module **/

import {FilterMenu} from "@web/search/filter_menu/filter_menu";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";
import {onWillStart} from "@odoo/owl";

patch(FilterMenu.prototype, "web_filter_groups.FilterMenu", {
    setup() {
        this._super.apply(this, arguments);
        this.user = useService("user");
        onWillStart(async () => {
            this.showFilter = await this.user.hasGroup(
                "web_filter_groups.filter_group"
            );
        });
    },
});
