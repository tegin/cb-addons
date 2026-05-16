from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class RestrictedPortalAccount(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "commission_count" in counters:
            commission_count = (
                request.env["account.invoice.line.agent"].search_count([])
                if request.env["account.invoice.line.agent"].check_access_rights(
                    "read", raise_exception=False
                )
                else 0
            )
            values["commission_count"] = commission_count
        return values

    @http.route(
        ["/my/invoices", "/my/invoices/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_invoices(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_my_invoices_values(
            page, date_begin, date_end, sortby, filterby
        )

        # pager
        pager = portal_pager(**values["pager"])

        # content according to pager and archive selected
        invoices = values["invoices"](pager["offset"])
        request.session["my_invoices_history"] = invoices.ids[:100]

        values.update(
            {
                "invoices": invoices,
                "pager": pager,
            }
        )

        return request.render(
            "account_portal_commission.portal_my_invoices_restricted", values
        )

    @http.route(["/my/commissions"], type="http", auth="user", website=True)
    def portal_my_commissions(self):
        settled_commission = request.env["account.invoice.line.agent"].search_read(
            [("settled", "=", True)], ["amount"]
        )
        unsettled_commission = request.env["account.invoice.line.agent"].search_read(
            [("settled", "=", False)], ["amount"]
        )
        settled_commission_ids = [x.get("id") for x in settled_commission]
        invoiced_settlement = request.env["commission.settlement.line"].search_read(
            [
                ("settlement_id.state", "=", "invoiced"),
                ("invoice_agent_line_id", "in", settled_commission_ids),
            ],
            ["settled_amount"],
        )
        paid_settlement = request.env["commission.settlement.line"].search_read(
            [
                ("settlement_id.invoice_id.payment_state", "=", "paid"),
                ("invoice_agent_line_id", "in", settled_commission_ids),
            ],
            ["settled_amount"],
        )

        values = {
            "settled_commissions": sum([x.get("amount") for x in settled_commission]),
            "unsettled_commissions": sum(
                [x.get("amount") for x in unsettled_commission]
            ),
            "invoiced_settlement": sum(
                [x.get("settled_amount") for x in invoiced_settlement]
            ),
            "paid_settlement": sum([x.get("settled_amount") for x in paid_settlement]),
            "currency_id": request.env.company.currency_id,
        }
        return request.render("account_portal_commission.portal_my_commissions", values)
