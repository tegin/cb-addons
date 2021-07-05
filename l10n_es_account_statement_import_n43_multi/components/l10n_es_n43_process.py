# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.core import Component


class L10nEsN43Process(Component):
    _name = "edi.output.l10n_es_n43.process"
    _inherit = "edi.component.input.mixin"
    _usage = "input.process"
    _backend_type = "l10n_es_n43"

    def process(self):
        self.env["account.bank.statement.import"].create(
            {
                "attachment_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.exchange_record.exchange_filename,
                            "datas": base64.b64encode(
                                self.exchange_record._get_file_content().encode(
                                    "utf-8"
                                ),
                            ),
                        },
                    )
                ]
            }
        ).with_context(journal_id=self.exchange_record.record.id).import_file()
