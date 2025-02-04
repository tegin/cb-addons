# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class AccountMoveMailListener(Component):
    _name = "account.move.storage.listener"
    _inherit = "base.event.listener"
    _apply_on = ["account.move"]

    def _get_exchange_record_vals(self, record):
        return {
            "model": record._name,
            "res_id": record.id,
        }

    def on_post_account_move(self, records):
        for record in records:
            if record.edi_disable_auto:
                continue
            partner = record.partner_id
            if record.move_type not in ["out_invoice", "out_refund"]:
                continue
            exchange_type = partner.with_company(
                record.company_id
            ).account_invoice_storage_exchange_type_id
            if not exchange_type:
                continue
            backend = exchange_type.backend_id
            if not backend:
                continue
            exchange_type = exchange_type.code
            if record._has_exchange_record(exchange_type, backend):
                continue
            exchange_record = backend.create_record(
                exchange_type, self._get_exchange_record_vals(record)
            )
            if record.partner_id.account_invoice_storage_clean_file_name:
                filename = exchange_record.exchange_filename
                exchange_record.exchange_filename = filename.replace("/", "-")
            backend.exchange_generate(exchange_record)
            backend.exchange_send(exchange_record)

    def on_generate_account_edi(self, records):
        return self.on_post_account_move(records)
