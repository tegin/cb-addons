/** @odoo-module **/

import {WebClient} from "@web/webclient/webclient";
import {patch} from "@web/core/utils/patch";

patch(WebClient.prototype, "web_single_app_logo.WebClient", {});
