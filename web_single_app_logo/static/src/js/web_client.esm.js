/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {WebClient} from "@web/webclient/webclient";

patch(WebClient.prototype, "web_single_app_logo.WebClient", {});
